
# src/tools/order_tool.py

from copy import deepcopy
from typing import Optional


DEFAULT_ORDERS = {
    "ORD1001": {
        "order_id": "ORD1001",
        "user_id": "U001",
        "amount": 199.00,
        "payment_status": "PAID",
        "refund_status": "NOT_REFUNDED"
    },
    "ORD1002": {
        "order_id": "ORD1002",
        "user_id": "U002",
        "amount": 299.00,
        "payment_status": "UNPAID",
        "refund_status": "NOT_REFUNDED"
    },
    "ORD1003": {
        "order_id": "ORD1003",
        "user_id": "U001",
        "amount": 399.00,
        "payment_status": "PAID",
        "refund_status": "REFUNDED"
    },
    "ORD1004": {
        "order_id": "ORD1004",
        "user_id": "U003",
        "amount": 599.00,
        "payment_status": "PAID",
        "refund_status": "NOT_REFUNDED"
    }
}


class OrderTool:
    """订单查询工具。"""

    def __init__(self,orders: Optional[dict] = None):
        # 每个独立测试环境使用自己的订单数据
        self.orders = deepcopy(
            DEFAULT_ORDERS if orders is None else orders
        )

    def query_order(self, order_id: str) -> dict:
        """根据订单号查询订单。"""

        if not isinstance(order_id, str) or not order_id.strip():
            return {
                "success": False,
                "error": "订单号不能为空"
            }

        order = self.orders.get(order_id)

        if order is None:
            return {
                "success": False,
                "error": f"订单不存在：{order_id}"
            }

        return {
            "success": True,
            "data": deepcopy(order)
        }
