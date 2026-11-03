
# src/agent/agent.py

import re
from typing import Any

from src.agent.state import AgentState


class PaymentAgent:
    """最小电商支付 Agent 执行框架。"""

    def __init__(self, tools: dict[str, Any]):
        self.tools = tools

    def _extract_order_id(
        self,
        user_input: str
    ) -> str | None:
        """从用户输入中提取订单号。"""

        match = re.search(
            r"ORD\d+",
            user_input,
            re.IGNORECASE
        )

        return match.group(0).upper() if match else None

    def _record_tool_call(
        self,
        state: AgentState,
        tool_name: str,
        arguments: dict
    ) -> None:
        """记录真实工具调用信息。"""

        state.add_tool_call(
            tool_name=tool_name,
            arguments=arguments
        )

        state.add_trace(
            "tool_call",
            tool_name=tool_name,
            arguments=arguments.copy()
        )

    def _finish(
        self,
        state: AgentState,
        response: str,
        status: str = "success"
    ) -> AgentState:
        """统一结束 Agent 执行。"""

        state.final_response = response
        state.status = status

        state.add_trace(
            "final_response",
            content=response,
            status=status
        )

        return state

    def run(
        self,
        user_id: str,
        user_input: str
    ) -> AgentState:
        """执行一次 Agent 任务。"""

        state = AgentState(
            user_id=user_id,
            user_input=user_input
        )

        try:
            # ==========================
            # 1. Planning：任务规划
            # ==========================

            order_id = self._extract_order_id(
                user_input
            )

            state.order_id = order_id

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

            is_refund = any(
                keyword in user_input
                for keyword in ["退款", "退掉", "退还"]
            )

            action = (
                "refund"
                if is_refund
                else "query_order"
            )

            state.add_trace(
                "planning",
                action=action,
                order_id=order_id
            )

            # ==========================
            # 2. 查询订单
            # ==========================

            order_tool = self.tools["order"]

            arguments = {
                "order_id": order_id
            }

            self._record_tool_call(
                state,
                "query_order",
                arguments
            )

            order_result = order_tool.query_order(
                **arguments
            )

            state.add_trace(
                "observation",
                tool_name="query_order",
                result=order_result
            )

            if not order_result["success"]:
                state.error = order_result["error"]

                return self._finish(
                    state,
                    order_result["error"],
                    "failed"
                )

            state.order_data = order_result["data"]

            # ==========================
            # 3. 查询任务：直接返回结果
            # ==========================

            if action == "query_order":

                payment_status = (
                    state.order_data["payment_status"]
                )

                refund_status = (
                    state.order_data["refund_status"]
                )

                response = (
                    f"订单 {order_id} 查询成功，"
                    f"支付状态：{payment_status}，"
                    f"退款状态：{refund_status}"
                )

                return self._finish(
                    state,
                    response
                )

            # ==========================
            # 4. Permission：权限检查
            # ==========================

            permission_tool = self.tools["permission"]

            permission_args = {
                "user_id": user_id,
                "order": state.order_data
            }

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
                    **permission_args
                )
            )

            state.add_trace(
                "observation",
                tool_name="check_permission",
                result=permission_result
            )

            if not permission_result["success"]:
                state.error = permission_result["error"]

                return self._finish(
                    state,
                    permission_result["error"],
                    "failed"
                )

            if not permission_result["allowed"]:
                state.error = "用户无权退款"

                return self._finish(
                    state,
                    "退款失败：用户无权操作该订单",
                    "failed"
                )

            # ==========================
            # 5. Refund：执行退款
            # ==========================

            refund_tool = self.tools["refund"]

            refund_args = {
                "user_id": user_id,
                "order_id": order_id
            }

            self._record_tool_call(
                state,
                "execute_refund",
                refund_args
            )

            refund_result = (
                refund_tool.execute_refund(
                    **refund_args
                )
            )

            state.add_trace(
                "observation",
                tool_name="execute_refund",
                result=refund_result
            )

            if not refund_result["success"]:
                state.error = refund_result["error"]

                return self._finish(
                    state,
                    f"退款失败：{refund_result['error']}",
                    "failed"
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
