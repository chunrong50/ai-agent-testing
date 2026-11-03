
# src/tools/refund_tool.py

from typing import Any


class RefundTool:
    """模拟退款执行工具。"""

    def __init__(self, orders: dict[str, dict[str, Any]]):
        # 与 OrderTool 使用同一份订单数据
        self.orders = orders

    def execute_refund(
        self,
        user_id: str,
        order_id: str
    ) -> dict:
        """执行退款，并进行服务端业务校验。"""

        order = self.orders.get(order_id)

        # 1. 检查订单是否存在
        if order is None:
            return {
                "success": False,
                "error": "订单不存在"
            }

        # 2. 再次检查订单所属人
        if order.get("user_id") != user_id:
            return {
                "success": False,
                "error": "无权退款：订单不属于当前用户"
            }

        # 3. 检查支付状态
        if order.get("payment_status") != "PAID":
            return {
                "success": False,
                "error": "订单未支付，不能退款"
            }

        # 4. 检查退款状态
        if order.get("refund_status") == "REFUNDED":
            return {
                "success": False,
                "error": "订单已经退款，不能重复退款"
            }

        if order.get("refund_status") != "NOT_REFUNDED":
            return {
                "success": False,
                "error": "订单退款状态异常"
            }

        # 5. 模拟退款成功
        order["refund_status"] = "REFUNDED"

        return {
            "success": True,
            "order_id": order_id,
            "refund_amount": order["amount"],
            "refund_status": "REFUNDED",
            "message": "退款成功"
        }
