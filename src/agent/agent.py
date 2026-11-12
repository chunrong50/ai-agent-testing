
# src/agent/agent.py

import re
from typing import Any, Optional

from src.agent.state import AgentState


# 根据关键字来决定执行流程

class PaymentAgent:
    """最小电商支付 Agent 执行框架。"""

    # 退款意图关键词（抽成类常量，便于维护和测试）
    REFUND_KEYWORDS = ("退款", "退掉", "退还", "取消订单", "取消支付")
    # 查询类关键词：出现这些时即使含"退款"也走查询（例如查询退款状态）
    QUERY_KEYWORDS = ("查询", "状态", "退款状态", "退款成功")

    # 初始化agent可以使用的工具
    def __init__(self, tools: dict[str, Any]):
        self.tools = tools

    def _extract_order_id(self,user_input: str) -> Optional[str]:
        """从用户输入中提取订单号。"""
        match = re.search(
            r"ORD\d+",
            user_input,
            re.IGNORECASE
        )

        return match.group(0).upper() if match else None

    def _record_tool_call(self,state: AgentState,tool_name: str,arguments: dict) -> None:
        """记录尝试真实工具调用信息。"""
        state.add_tool_call(
            tool_name=tool_name,
            arguments=arguments
        )

        state.add_trace(
            "tool_call",
            tool_name=tool_name,
            arguments=arguments.copy()
        )

    def _finish( self,state: AgentState,response: str,status: str = "success") -> AgentState:
        """统一结束 Agent 执行。"""
        state.final_response = response
        state.status = status

        state.add_trace(
            "final_response",
            content=response,
            status=status
        )

        return state

    def is_refund_intent(self, user_input: str) -> bool:
        """判断用户输入是否表达退款意图（排除查询类表述）。"""
        return (
                any(k in user_input for k in self.REFUND_KEYWORDS)
                and not any(k in user_input for k in self.QUERY_KEYWORDS)
        )

    def _decide_action(self, user_input: str) -> str:
        """判断动作：refund 或 query_order。"""
        # 明确查询意图优先，避免"查询退款状态"被误判为退款
        if self.is_refund_intent(user_input):
            return "refund"
        return "query_order"




    def run(self,user_id: str,user_input: str) -> AgentState:
        """执行一次 Agent 任务。"""

        state = AgentState(user_id=user_id,user_input=user_input)

        try:
            # ==========================
            # 1. Planning：任务规划
            # ==========================

            order_id = self._extract_order_id(user_input)

            state.order_id = order_id

            # 检查订单号
            if order_id is None:
                state.add_trace(
                    "planning",
                    action="unknown",
                    reason="没有识别到订单号"
                )

                return self._finish(
                    state,
                    "请提供正确的订单号",
                    "failed"
                )

            # 如果包含退款语义就认定需要退款，否则走订单查询
            action = self._decide_action(user_input)
            state.add_trace("planning", action=action, order_id=order_id)   # 追加状态记录->下一步的执行的工具


            # ==========================
            # 2. 查询订单
            # ==========================

            # 拿到订单工具
            order_tool = self.tools["order"]

            arguments = {"order_id": order_id}

            # 记录订单查询准备调用
            self._record_tool_call(state,"query_order",arguments)

            # 调用订单工具
            order_result = order_tool.query_order(**arguments)

            # 记录订单工具返回的结果
            state.add_trace(
                "observation",
                tool_name="query_order",
                result=order_result
            )


            # 先判断 success，再访问 data，避免 KeyError
            if not order_result["success"]:
                state.error = order_result.get("error","订单查询失败")
                return self._finish(state,state.error,"failed")

            order_data = order_result["data"]


            # 订单不属于当前用户
            if order_data.get("user_id") !=user_id:
                error = f"订单{order_id}不属于当前用户{user_id}"
                state.error = error
                return self._finish(
                    state,
                    error,
                    "failed"
                )


            state.order_data = order_data

            # ==========================
            # 3. 获取查询订单的结果，并返回state和工具的response
            # ==========================

            if action == "query_order":
                response = (
                    f"订单 {order_id} 查询成功，"
                    f"支付状态：{order_data['payment_status']}，"
                    f"退款状态：{order_data['refund_status']}"
                )

                return self._finish(
                    state,
                    response
                )

            # ==========================
            # 4. Permission：权限检查
            # ==========================

            permission_tool = self.tools["permission"]
            self._record_tool_call(
                state,
                "check_permission",
                {
                    "user_id": user_id,
                    "order_id": order_id
                }
            )

            permission_result = (
                permission_tool.check_permission(
                    user_id=user_id,
                    order=order_data
                )
            )

            state.add_trace(
                "observation",
                tool_name="check_permission",
                result=permission_result
            )

            if not permission_result["success"]:
                state.error = permission_result.get("error","权限校验失败")
                return self._finish(state, state.error, "failed")

            if not permission_result["allowed"]:
                state.error = "用户无权退款"
                return self._finish(state, "退款失败：用户无权操作该订单", "failed")

            # ==========================
            # 5. Refund：执行退款
            # ==========================

            refund_tool = self.tools["refund"]
            refund_args = {"user_id": user_id, "order_id": order_id}
            self._record_tool_call(state, "execute_refund", refund_args)

            refund_result = refund_tool.execute_refund(**refund_args)

            state.add_trace("observation",tool_name="execute_refund", result=refund_result)

            if not refund_result["success"]:
                state.error =  refund_result.get("error", "退款失败")

                return self._finish(
                    state, f"退款失败：{state.error}", "failed"
                )
            return self._finish(
                state,
                f"订单 {order_id} 退款成功，"
                f"退款金额：{refund_result['refund_amount']:.2f}"
            )

        except Exception as exc:
            # ==========================
            # 6. 异常处理
            # ==========================

            state.error = str(exc)

            state.add_trace(
                "error",
                error_type=type(exc).__name__,
                message=str(exc)
            )

            return self._finish(
                state,
                "系统执行异常，请稍后重试",
                "failed"
            )
