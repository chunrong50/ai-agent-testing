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

# 加载.env文件
# load_dotenv()
# api_key = os.getenv("DEEPSEEK_API_KEY")
# base_url = os.getenv("DEEPSEEK_BASE_URL")
# print(api_key)