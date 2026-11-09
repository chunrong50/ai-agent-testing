import os
from dotenv import load_dotenv

class MockOrderTool:

    def __init__(self, response):
        self.response = response
        self.call_count = 0
        self.called_order_id = None

    def query_order(self, order_id):
        self.call_count += 1
        self.called_order_id = order_id
        return self.response



def text_response(content):
    # 模拟LLM的文本响应结果
    return {"tool_calls": [], "content": content}

def tool_response(name,order_id):
    # 模拟LLM的响应结果中包含tool_calls，工具调用

    return {
    "tool_calls": [
        {
            "name": f"{name}",
            "arguments": {
                "order_id": f"{order_id}"
            }
        }
    ],
    "content": None
}


def tool_response_exception(name, order_id):
    return {
    "tool_calls": [
        {
            "name": f"{name}",
            "arguments": {
            }
        }
    ],
    "content": None
}

