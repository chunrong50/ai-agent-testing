query_order_schema = {
    "type": "function",
    "function": {
        "name": "query_order",
        "description": "根据订单号查询订单信息",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "订单编号"
                }
            },
            "required": ["order_id"]
        }
    }
}

execute_refund_schema = {
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
            "required": ["order_id"]

        },
    },
}

schemas = [query_order_schema,execute_refund_schema]

def get_schema(name):
    for schema in schemas:
        if schema["function"]["name"] == name:
            return schema["function"]
        else:
            return None
