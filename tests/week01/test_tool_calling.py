# tests/week02/test_tool_calling.py
"""Day 5 测试：用 FakeLLM 脚本化模拟 LLM 返回，测试稳定、免费、可重复。

测什么：Agent 对 LLM 返回的 tool_calls 的处理（解析 / 校验 / 执行 / 安全控制）。
不测：真实模型会不会选对工具 -> 见文件末尾的 Smoke Test（需 LLM_API_KEY）。
Tools 使用 Day 4 的真实 OrderTool / PermissionTool / RefundTool。
"""
import json
import os

import pytest

from src.agent.llm_agent import LLMAgent, LLMResponse, OpenAICompatibleLLM, ToolCall
from src.schemas.tool_schemas import TOOL_SCHEMAS
from src.tools.order_tool import OrderTool
from src.tools.permission_tool import PermissionTool
from src.tools.refund_tool import RefundTool


# ------------------------------ Fake LLM ------------------------------
class FakeLLM:
    """按顺序返回预设响应，并记录每次收到的 messages / tools。"""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def chat(self, messages, tools=None):
        self.calls.append({"messages": [dict(m) for m in messages], "tools": tools})
        return self.responses.pop(0)


def tool_resp(name, args, call_id="call_1"):
    # 定义LLM的工具响应
    raw = args if isinstance(args, str) else json.dumps(args)
    return LLMResponse(tool_calls=[ToolCall(id=call_id, name=name, arguments=raw)])


def text_resp(text):
    # 定义LLM的文本响应
    return LLMResponse(content=text)


# ------------------------------ Spy Tools ------------------------------
class SpyRefundTool(RefundTool):
    """记录是否真的被调用。"""

    def __init__(self, orders):
        super().__init__(orders)
        self.calls = []

    def execute_refund(self, user_id, order_id):
        self.calls.append((user_id, order_id))
        return super().execute_refund(user_id, order_id)


class DenyPermissionTool(PermissionTool):
    """模拟权限服务判定无权限。"""

    def check_permission(self, user_id, order):
        return {"success": True, "allowed": False, "reason": "无权"}


class BrokenOrderTool(OrderTool):
    def query_order(self, order_id):
        raise TimeoutError("db timeout")


@pytest.fixture
def env():
    order_tool = OrderTool()
    refund_tool = SpyRefundTool(order_tool.orders)  # 与 OrderTool 共用同一份订单数据
    tools = {"order": order_tool, "permission": PermissionTool(), "refund": refund_tool}
    return {"tools": tools, "orders": order_tool.orders, "refund": refund_tool}


def make_agent(env, responses, tools=None):
    llm = FakeLLM(responses)
    return LLMAgent(llm, tools or env["tools"]), llm


def tool_names(state):
    return [c["tool_name"] for c in state.tool_calls]


# ================================ 4 个核心用例 ================================
def test_tc01_query_order_selects_query_tool_with_correct_args(env):
    agent, llm = make_agent(env, [
        tool_resp("query_order", {"order_id": "ORD1001"}),
        text_resp("订单 ORD1001 已支付，未退款。"),
    ])
    state = agent.run("U001", "帮我查一下订单 ORD1001")

    assert state.tool_calls == [{"tool_name": "query_order", "arguments": {"order_id": "ORD1001"}}]
    assert env["refund"].calls == []                      # 查询不应触发退款
    assert state.status == "success" and state.error is None
    assert state.final_response == "订单 ORD1001 已支付，未退款。"
    # 第一次请求带了 Schema；第二次请求带回了工具 Observation
    assert llm.calls[0]["tools"] == TOOL_SCHEMAS
    last = llm.calls[1]["messages"][-1]
    assert last["role"] == "tool" and last["tool_call_id"] == "call_1"
    assert "ORD1001" in last["content"]


def test_tc02_refund_selects_refund_tool_and_runs_full_safety_chain(env):
    agent, _ = make_agent(env, [
        tool_resp("execute_refund", {"order_id": "ORD1001"}),
        text_resp("退款成功"),
    ])
    state = agent.run("U001", "帮我退款 ORD1001")

    # LLM 选 execute_refund 后，Agent 仍按 查订单 -> 权限 -> 退款 的顺序执行
    assert tool_names(state) == ["query_order", "check_permission", "execute_refund"]
    assert state.tool_calls[-1]["arguments"] == {"user_id": "U001", "order_id": "ORD1001"}
    assert env["orders"]["ORD1001"]["refund_status"] == "REFUNDED"
    assert state.status == "success" and state.error is None


def test_tc03_refund_status_query_must_not_execute_refund(env):
    # 正确的 LLM 行为：查询退款状态 -> query_order
    agent, _ = make_agent(env, [
        tool_resp("query_order", {"order_id": "ORD1003"}),
        text_resp("订单 ORD1003 已退款。"),
    ])
    state = agent.run("U001", "ORD1003 的退款到账了吗？")

    assert "execute_refund" not in tool_names(state)
    assert env["refund"].calls == []


def test_tc04_unknown_tool_is_rejected_and_logged(env):
    agent, _ = make_agent(env, [
        tool_resp("delete_all_orders", {"order_id": "ORD1001"}),   # LLM 幻觉出的工具
        text_resp("抱歉，无法完成该操作。"),
    ])
    state = agent.run("U001", "帮我处理订单 ORD1001")

    assert state.tool_calls == []                                  # 没有任何真实工具被调用
    assert "UNKNOWN_TOOL" in state.error
    errors = [t for t in state.trace if t["type"] == "error"]
    assert errors and errors[0]["error_type"] == "UNKNOWN_TOOL" and errors[0]["tool_name"] == "delete_all_orders"
    assert state.status == "failed"
    assert state.final_response == "抱歉，无法完成该操作。"        # Agent 没崩，仍给出回复


# ================================ 加分用例 ================================
def test_refund_other_users_order_is_blocked_even_if_llm_chooses_refund(env):
    """U001 退 U003 的订单：LLM 选了退款，也必须被拦截。"""
    agent, _ = make_agent(env, [
        tool_resp("execute_refund", {"order_id": "ORD1004"}),
        text_resp("无法退款"),
    ])
    state = agent.run("U001", "退款 ORD1004")

    assert env["refund"].calls == []
    assert env["orders"]["ORD1004"]["refund_status"] == "NOT_REFUNDED"
    assert "不属于当前用户" in state.error and state.status == "failed"


def test_permission_denied_blocks_refund(env):
    """纵深防御：即使订单归属通过，PermissionTool 拒绝时也不能退款。"""
    tools = {**env["tools"], "permission": DenyPermissionTool()}
    agent, _ = make_agent(env, [tool_resp("execute_refund", {"order_id": "ORD1001"}),
                                text_resp("您无权退款")], tools)
    state = agent.run("U001", "退款 ORD1001")

    assert tool_names(state) == ["query_order", "check_permission"]
    assert env["refund"].calls == []
    assert state.error == "用户无权操作该订单"


@pytest.mark.parametrize("user_id, order_id, expected_error", [
    ("U001", "ORD1003", "已经退款"),     # 重复退款
    ("U002", "ORD1002", "未支付"),       # 未支付订单
    ("U001", "ORD9999", "订单不存在"),   # 订单不存在
])
def test_business_rules_still_enforced(env, user_id, order_id, expected_error):
    agent, _ = make_agent(env, [tool_resp("execute_refund", {"order_id": order_id}),
                                text_resp("退款失败")])
    state = agent.run(user_id, f"退款 {order_id}")
    assert expected_error in state.error and state.status == "failed"


@pytest.mark.parametrize("bad_args, case", [
    ("{not json", "非法 JSON"),
    ({}, "缺少 order_id"),
    ({"order_id": 123}, "类型错误"),
    ({"order_id": "  "}, "空字符串"),
    ({"order_id": "ORD1003", "user_id": "U003"}, "LLM 试图自带 user_id"),
])
def test_invalid_arguments_are_rejected_without_calling_tool(env, bad_args, case):
    agent, _ = make_agent(env, [tool_resp("execute_refund", bad_args), text_resp("参数有误")])
    state = agent.run("U001", "退款")

    assert "INVALID_ARGUMENTS" in state.error, case
    assert state.tool_calls == [] and env["refund"].calls == []


def test_tool_exception_is_caught_and_fed_back_to_llm(env):
    tools = {**env["tools"], "order": BrokenOrderTool()}
    agent, llm = make_agent(env, [tool_resp("query_order", {"order_id": "ORD1001"}),
                                  text_resp("系统繁忙，请稍后再试。")], tools)
    state = agent.run("U001", "查订单 ORD1001")

    assert "TOOL_EXCEPTION" in state.error
    assert "TOOL_EXCEPTION" in llm.calls[1]["messages"][-1]["content"]
    assert state.final_response == "系统繁忙，请稍后再试。"


def test_multiple_tool_calls_in_one_response_all_executed(env):
    multi = LLMResponse(tool_calls=[
        ToolCall("c1", "query_order", json.dumps({"order_id": "ORD1001"})),
        ToolCall("c2", "query_order", json.dumps({"order_id": "ORD1003"})),
    ])
    agent, llm = make_agent(env, [multi, text_resp("两个订单都查到了")])
    state = agent.run("U001", "查 ORD1001 和 ORD1003")

    assert [c["arguments"]["order_id"] for c in state.tool_calls] == ["ORD1001", "ORD1003"]
    tool_msgs = [m for m in llm.calls[1]["messages"] if m["role"] == "tool"]
    assert [m["tool_call_id"] for m in tool_msgs] == ["c1", "c2"]


def test_max_steps_prevents_infinite_tool_loop(env):
    looping = [tool_resp("query_order", {"order_id": "ORD1001"}, f"c{i}") for i in range(10)]
    agent, _ = make_agent(env, looping)
    agent.max_steps = 3
    state = agent.run("U001", "查订单")

    assert state.status == "failed" and "最大工具调用轮数" in state.error
    assert len(state.tool_calls) == 3


def test_llm_exception_is_handled(env):
    class BoomLLM:
        def chat(self, messages, tools=None):
            raise ConnectionError("llm down")

    state = LLMAgent(BoomLLM(), env["tools"]).run("U001", "查订单 ORD1001")
    assert state.status == "failed" and state.final_response == "系统执行异常，请稍后重试"


from dotenv import load_dotenv
load_dotenv()
# ============================ Smoke Test（真实 LLM）============================
@pytest.mark.skipif(not os.getenv("LLM_API_KEY"), reason="需要设置 LLM_API_KEY")     #真实调用时使用：DEEPSEEK_API_KEY
def test_smoke_real_llm_selects_query_order(env):
    agent = LLMAgent(OpenAICompatibleLLM(), env["tools"])
    state = agent.run("U001", "帮我查一下订单 ORD1001 的状态")

    assert state.tool_calls and state.tool_calls[0] == {
        "tool_name": "query_order", "arguments": {"order_id": "ORD1001"}}
    assert env["refund"].calls == []