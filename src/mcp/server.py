# 简化的 server.py，要求：
# 1. 提供 query_order(order_id) 方法。
# 2. 提供 execute_refund(order_id) 方法。
# 3. 提供 list_tools() 方法，返回 Server 暴露的工具名称。

class Server:
    def __init__(self,tools):
        self.tools = tools

    def  query_order(self,order_id):
        return self.tools.query_order(order_id)

    def execute_refund(self,order):
        return self.tools.execute_refund(order)

    def list_tools(self):
        return self.tools