# src/agent/llm_agent.py
"""Day 5: LLM Tool Calling Agent。

职责划分：
- LLM  ：理解意图，决定调用哪个工具、生成参数（只返回 tool_calls，不执行任何代码）
- Agent：解析 tool_calls，做白名单/参数校验，执行 Python Tool，把 Observation 回传给 LLM
- Tool ：真正的业务逻辑（OrderTool / PermissionTool / RefundTool，直接复用 Day 4）

与 Day 4 的区别：Day 4 用关键词规则决定调用哪个工具；Day 5 由 LLM 决定。
安全控制不变：退款前必须 查订单 -> 订单归属 -> PermissionTool -> RefundTool。
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Optional, Protocol

from src.agent.agent import PaymentAgent
from src.agent.state import AgentState
from src.schemas.tool_schemas import ALLOWED_TOOL_NAMES, TOOL_SCHEMAS, get_schema

SYSTEM_PROMPT = (
    "你是电商支付客服助手。根据用户意图选择合适的工具。"
    "只有用户明确要求退款时才调用 execute_refund；"
    "查询订单、查询退款状态请使用 query_order。"
    "工具返回错误时，如实告知用户，不要编造结果。"
)


# ---------------------------------------------------------------------------
# 与模型供应商解耦的数据结构
# （注意：src/llm_client.py 里已有 LLMClient 类，这里叫 ToolCallingLLM 避免重名）
# ---------------------------------------------------------------------------
@dataclass
class ToolCall:
    id: str
    name: str
    arguments: str  # LLM 返回的是 JSON 字符串，需要 Agent 自己解析


@dataclass
class LLMResponse:
    # LLM 的响应，包含可选的文本内容 content 和工具调用列表 tool_calls
    content: Optional[str] = None
    tool_calls: list[ToolCall] = field(default_factory=list)


class ToolCallingLLM(Protocol):
    # 理解为可以进行工具调用的LLM
    def chat(self, messages: list[dict], tools: Optional[list[dict]] = None) -> LLMResponse: ... # ... Protocol协议的占位


class OpenAICompatibleLLM:
    """真实模型适配器（OpenAI 兼容接口：OpenAI / DeepSeek / 通义千问等），仅 Smoke Test 使用。

    环境变量：LLM_API_KEY（必需）、LLM_BASE_URL、LLM_MODEL
    """

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None,
                 base_url: Optional[str] = None):
        from openai import OpenAI  # 延迟导入，单元测试不需要安装 openai

        self.client = OpenAI(api_key=api_key or os.environ["DEEPSEEK_API_KEY"],
                             base_url=base_url or os.getenv("DEEPSEEK_BASE_URL"))
        self.model = model or os.getenv("DEEPSEEK_MODEL", "gpt-4o-mini")

    def chat(self, messages: list[dict], tools: Optional[list[dict]] = None) -> LLMResponse:
        kwargs: dict[str, Any] = {"model": self.model, "messages": messages, "temperature": 0}
        if tools:
            kwargs["tools"] = tools
        msg = self.client.chat.completions.create(**kwargs).choices[0].message
        calls = [ToolCall(id=tc.id, name=tc.function.name, arguments=tc.function.arguments or "{}")
                 for tc in (msg.tool_calls or [])]
        return LLMResponse(content=msg.content, tool_calls=calls)


# ---------------------------------------------------------------------------
# LLM Agent：继承 PaymentAgent，复用 _finish / _record_tool_call / AgentState
# ---------------------------------------------------------------------------
class LLMAgent(PaymentAgent):
    def __init__(self, llm: ToolCallingLLM, tools: dict[str, Any],
                 max_steps: int = 5, system_prompt: str = SYSTEM_PROMPT):
        super().__init__(tools)  # tools = {"order":..., "permission":..., "refund":...}
        self.llm = llm
        self.max_steps = max_steps
        self.system_prompt = system_prompt
        # Schema 中的工具名 -> 真正执行的 Python 方法
        self._handlers = {
            "query_order": self._tool_query_order,
            "execute_refund": self._tool_execute_refund,
        }

    # ------------------------------------------------------------------ run
    def run(self, user_id: str, user_input: str) -> AgentState:
        state = AgentState(user_id=user_id, user_input=user_input)
        messages: list[dict] = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_input},
        ]

        try:
            for _ in range(self.max_steps):  #  Agent与 LLM 的对话轮次（conversation turn）
                # 第 1 轮：发消息给 LLM → LLM 返回 tool_calls → Agent 执行工具 → 把结果追加到 messages
                # 第 2 轮：把"带工具结果的完整 messages"再发给 LLM → LLM 可能基于结果继续调用工具，或给出最终回复
                # 第 3 轮：...
                # 循环就是让 LLM 基于工具结果持续决策的机制。
                response = self.llm.chat(messages=messages, tools=TOOL_SCHEMAS)
                state.add_trace("llm_response", content=response.content,
                                tool_calls=[tc.name for tc in response.tool_calls])

                # 没有 tool_calls => LLM 给出最终回复
                if not response.tool_calls:
                    return self._finish(state, response.content or "",
                                        "failed" if state.error else "success")

                # 先把 assistant 的 tool_calls 放回历史（OpenAI 协议要求）
                messages.append({
                    "role": "assistant", "content": response.content,
                    "tool_calls": [{"id": tc.id, "type": "function",
                                    "function": {"name": tc.name, "arguments": tc.arguments}}
                                   for tc in response.tool_calls],
                })
                # 逐个执行，并把 Observation 回传给 LLM
                for tc in response.tool_calls:
                    observation = self.execute_tool(state, user_id, tc)
                    messages.append({"role": "tool", "tool_call_id": tc.id,
                                     "content": json.dumps(observation, ensure_ascii=False)})

            state.error = "超过最大工具调用轮数"
            state.add_trace("error", error_type="MaxStepsExceeded", message=state.error)
            return self._finish(state, "系统执行异常，请稍后重试", "failed")

        except Exception as exc:  # LLM 接口本身异常（超时/500 等）
            state.error = str(exc)
            state.add_trace("error", error_type=type(exc).__name__, message=str(exc))
            return self._finish(state, "系统执行异常，请稍后重试", "failed")

    # --------------------------------------------------- 单个工具调用的校验+执行
    def execute_tool(self, state: AgentState, user_id: str, tool_call: ToolCall) -> dict:
        name = tool_call.name

        # 1. 白名单：LLM 可能幻觉出不存在的工具
        if name not in ALLOWED_TOOL_NAMES or name not in self._handlers:
            return self._reject(state, name, "UNKNOWN_TOOL", f"工具不存在：{name}")

        # 2. 参数必须是合法 JSON object
        try:
            args = json.loads(tool_call.arguments or "{}")
        except json.JSONDecodeError:
            return self._reject(state, name, "INVALID_ARGUMENTS", "参数不是合法 JSON")
        if not isinstance(args, dict):
            return self._reject(state, name, "INVALID_ARGUMENTS", "参数必须是 JSON 对象")

        # 3. Schema 校验：必填 / 类型 / 多余字段（含 LLM 自带 user_id）
        error = self._validate_args(name, args)
        if error:
            return self._reject(state, name, "INVALID_ARGUMENTS", error, args)

        # 4. 执行；user_id 来自会话，由 Agent 注入，绝不信任 LLM
        try:
            result = self._handlers[name](state, user_id, **args)
        except Exception as exc:  # 工具异常不能让 Agent 崩溃
            return self._reject(state, name, "TOOL_EXCEPTION",
                                f"{type(exc).__name__}: {exc}", args)

        if not result.get("success"):
            state.error = result.get("error", "工具执行失败")
        return result

    @staticmethod
    def _validate_args(name: str, args: dict) -> Optional[str]:
        params = get_schema(name)["function"]["parameters"]
        props = params.get("properties", {})
        for key in params.get("required", []):
            if key not in args:
                return f"缺少必填参数：{key}"
        for key, value in args.items():
            if key not in props:
                return f"不允许的参数：{key}"
            if props[key].get("type") == "string" and (not isinstance(value, str) or not value.strip()):
                return f"参数 {key} 必须是非空字符串"
        return None

    def _reject(self, state: AgentState, name: str, code: str, detail: str,
                args: Optional[dict] = None) -> dict:
        state.error = f"{code}: {detail}"
        state.add_trace("error", error_type=code, tool_name=name,
                        arguments=args or {}, message=detail)
        return {"success": False, "error": code, "detail": detail}

    # ------------------------------------------------------------ Tool 实现
    def _tool_query_order(self, state: AgentState, user_id: str, order_id: str) -> dict:
        arguments = {"order_id": order_id}
        self._record_tool_call(state, "query_order", arguments)
        result = self.tools["order"].query_order(**arguments)
        state.add_trace("observation", tool_name="query_order", result=result)

        if not result["success"]:
            return result
        # 订单不属于当前用户：不把订单内容返回给 LLM
        if result["data"].get("user_id") != user_id:
            return {"success": False, "error": f"订单{order_id}不属于当前用户{user_id}"}

        state.order_id = order_id
        state.order_data = result["data"]
        return result

    def _tool_execute_refund(self, state: AgentState, user_id: str, order_id: str) -> dict:
        """LLM 选了 execute_refund 也不能直接退款：查订单 -> 权限 -> RefundTool。"""
        # 1. 获取订单并校验归属
        order_result = self._tool_query_order(state, user_id, order_id)
        if not order_result["success"]:
            return order_result
        order_data = order_result["data"]

        # 2. PermissionTool 权限校验
        self._record_tool_call(state, "check_permission",
                               {"user_id": user_id, "order_id": order_id})
        permission = self.tools["permission"].check_permission(user_id=user_id, order=order_data)
        state.add_trace("observation", tool_name="check_permission", result=permission)
        if not permission["success"]:
            return {"success": False, "error": permission.get("error", "权限校验失败")}
        if not permission["allowed"]:
            return {"success": False, "error": "用户无权操作该订单"}

        # 3. RefundTool（内部还有 支付状态 / 重复退款 等业务规则校验）
        refund_args = {"user_id": user_id, "order_id": order_id}
        self._record_tool_call(state, "execute_refund", refund_args)
        refund_result = self.tools["refund"].execute_refund(**refund_args)
        state.add_trace("observation", tool_name="execute_refund", result=refund_result)
        return refund_result


# ---------------------------------------------------------------------------
# 默认装配：与 Day 4 相同的 Tools（RefundTool 必须与 OrderTool 共用同一份订单数据）
# ---------------------------------------------------------------------------
def build_default_agent(llm: Optional[ToolCallingLLM] = None,
                        orders: Optional[dict] = None) -> LLMAgent:
    from src.tools.order_tool import OrderTool
    from src.tools.permission_tool import PermissionTool
    from src.tools.refund_tool import RefundTool

    order_tool = OrderTool(orders)
    tools = {"order": order_tool,
             "permission": PermissionTool(),
             "refund": RefundTool(order_tool.orders)}
    return LLMAgent(llm or OpenAICompatibleLLM(), tools)