


class ToolExecutor:
    def __init__(self,tools):
        self.tools = tools

    def execute_tool(self,tool_name:str,user_id,order_id) -> dict:

        try:
            if tool_name == "query_order":
                tool_result = self.tools[tool_name].query_order(order_id)

            elif tool_name == "permission_check":
                order_result = self.tools["query_order"].orders.get(order_id)
                tool_result = self.tools[tool_name].check_permission(user_id, order_result)

            elif tool_name == "execute_refund":
                tool_result = self.tools[tool_name].execute_refund(user_id, order_id)
        except Exception as e:
            tool_result = {
                "success": False,
                "error": str(e)
            }



        return tool_result


