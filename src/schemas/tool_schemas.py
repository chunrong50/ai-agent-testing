"""Day 5: Tool Schema —— 给 LLM 看的"工具说明书"。

注意：Schema 只告诉 LLM 有哪些工具、怎么传参，
不代表权限控制。权限校验必须在 Python 后端完成。
格式为 OpenAI-compatible（OpenAI / DeepSeek / 通义千问 / Moonshot 等均支持）。
"""
from typing import Optional

QUERY_ORDER_SCHEMA = {
    "type": "function",
    "function": {
        "name": "query_order",
        "description": (
            "查询订单的详细信息和当前状态（包括是否已支付、是否已退款）。"
            "当用户想查看订单、查询订单状态或查询退款进度时使用。"
            "注意：这个工具只读，不会修改订单。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "订单编号，例如 ORD1001",
                }
            },
            "required": ["order_id"],
            "additionalProperties": False,
        },
    },
}

EXECUTE_REFUND_SCHEMA = {
    "type": "function",
    "function": {
        "name": "execute_refund",
        "description": (
            "对指定订单发起退款。仅当用户明确要求退款/退钱时使用；"
            "如果用户只是查询订单或退款状态，不要调用此工具。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "需要退款的订单编号，例如 ORD1001",
                }
            },
            "required": ["order_id"],
            "additionalProperties": False,
        },
    },
}

#
TOOL_SCHEMAS = [QUERY_ORDER_SCHEMA, EXECUTE_REFUND_SCHEMA]

# 白名单：Agent 只执行 Schema 中声明过的工具
ALLOWED_TOOL_NAMES = {s["function"]["name"] for s in TOOL_SCHEMAS}  # 编译器问题


def get_schema(name: str) -> Optional[dict]:
    """按工具名取 Schema，不存在返回 None。"""
    for s in TOOL_SCHEMAS:
        if s["function"]["name"] == name:
            return s
    return None