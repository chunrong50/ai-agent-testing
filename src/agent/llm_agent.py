import json

from agent.agent import PaymentAgent
from agent.state import AgentState
from schemas.tool_schemas import get_schema

SYSTEM_PROMPT = (
    "你是电商支付客服助手。根据用户意图选择合适的工具。"
    "只有用户明确要求退款时才调用 execute_refund；"
    "查询订单、查询退款状态请使用 query_order。"
    "工具返回错误时，如实告知用户，不要编造结果。"
)



class LLMToolAgent(PaymentAgent):

    def __init__(self,llm,tools,max_steps=5):
        """
               llm: 模拟或真实 LLM
               tools: 已注册的 Python 工具
               max_steps: 最大工具调用次数
               """
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps

    def run(self,user_id,user_input):
        """
         Agent 主执行入口
        :param user_input:
        :return:
        """
        state = AgentState(user_id=user_id, user_input=user_input)
        # 1. 初始化消息上下文
        messages:list[dict]=[{"role":"user","content": user_input},{"role": "system", "content": SYSTEM_PROMPT},]



        # 2. 进入 Tool Calling Loop
        for step in range(self.max_steps):

            # 3. 请求 LLM
            response=self.llm.chat(messages,tools=self.tools)


            # 4. 判断 LLM 是否要求调用工具
            if not response.get("tool_calls"):
                return response.get("content")

            # 5. 遍历 LLM 返回的工具调用
            for tool_call in response.get("tool_calls"):
                # 5.1 获取工具名称
                tool_name=tool_call["name"]
                # 5.2 获取工具参数
                args=tool_call["arguments"]

                 # 5.3 校验工具是否存在
                if not tool_name in self.tools:
                    return f"Error: Unknown tool: {tool_name}"

                # 5.4 校验工具参数
                param = get_schema("tool_name")["parameters"]
                required_params = param["required"]

                if not args:
                    return f"Error: tool '{tool_name}' arguments must not empty"

                for x in required_params:
                    if x not in args:
                        return f"Error: required {x} not in arguments"

                for arg in args:
                    if not arg in param:
                        return f"Error: arguments '{arg}' error"


                state.add_tool_call(tool_name, args)

                # 5.5 执行工具
                try:
                    tool_result = self.tools[tool_name](args)
                except Exception as e:
                    tool_result = {
                        "success": False,
                        "error": str(e)
                    }
                state.add_trace("tool_call",tool_result)

                # 6. 将 Observation 返回给 LLM
                messages.append({
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps(
                        tool_result,
                        ensure_ascii=False
                    )
                })

                # 7. 达到最大调用次数
            return "Error: Maximum tool calling steps reached"




