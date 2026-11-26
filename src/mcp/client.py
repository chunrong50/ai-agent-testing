from mcp.server import Server


class Client:
    def __init__(self,server):
        self.server = server

    def get_list_tools(self):
        return self.server.list_tools()

    def execute_tool(self,tool_name,arg):
        return self.server.execute_tool(tool_name,arg)



