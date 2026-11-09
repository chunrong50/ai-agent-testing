


class ToolExecutor:
    def __init__(self,tools):
        self.tools = tools

    def execute_tool(self,state,tool_name:str,user_id,args) -> dict:
        state.add_trace("tool call", tool_name=tool_name, result="准备开始工具调用")
        try:
            if tool_name == "query_order":
                tool_result = self.tools[tool_name].query_order(args["order_id"])

            elif tool_name == "permission_check":
                order_result = self.tools["query_order"].orders.get(args["order_id"])
                tool_result = self.tools[tool_name].check_permission(user_id, order_result)

            elif tool_name == "execute_refund":
                tool_result = self.tools[tool_name].execute_refund(user_id, args["order_id"])
        except Exception as e:
            tool_result = {
                "success": False,
                "error": str(e)
            }

        return tool_result


