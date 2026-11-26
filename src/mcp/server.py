# 简化的 server.py，要求：
# 1. 提供 query_order(order_id) 方法。
# 2. 提供 execute_refund(order_id) 方法。
# 3. 提供 list_tools() 方法，返回 Server 暴露的工具名称。

class Server:
    def __init__(self,tools):
        self.tools = tools

    def list_tools(self):
        return ["query_order", "execute_refund"]

    def query_order(self,order_id):
        return self.tools["query_order"].query_order(order_id)

    def execute_refund(self,order_id):
        return self.tools["execute_refund"].execute_refund(order_id)



    def execute_tool(self,tool_name,arg):
        # self.query_order 注意这里没有括号。 因此不会立即执行方法。
        # 然后再根据 tool_name,选择对应方法执行

        tools_map={"query_order":self.query_order,"execute_refund":self.execute_refund}

        return tools_map[tool_name](arg)