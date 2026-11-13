import json

from agent.llm_agent import LLMToolAgent
from agent.plan_manager import PlanManager
from agent.planning import Plan
from agent.state import AgentState
from agent.tool_executor import ToolExecutor
from schemas.tool_schemas import get_schema


SYSTEM_PROMPT = (
    "你是电商支付客服助手。根据用户意图选择合适的工具。"
    "只有用户明确要求退款时才调用 execute_refund；"
    "查询订单、查询退款状态请使用 query_order。"
    "工具返回错误时，如实告知用户，不要编造结果。"
)

TOOL_SCHEMAS = [
    get_schema("query_order"),
    get_schema("execute_refund"),
    get_schema("permission_check")
]


# 具有planning 能力的Agent

class LLMPlanAgent(LLMToolAgent):
    def __init__(self, llm,tools,max_steps=5):
        self.manager = PlanManager(Plan())
        self.tools = tools
        self.max_steps = max_steps
        super().__init__(llm,tools,max_steps)




    def run(self,user_id,user_input) -> AgentState:

        state=AgentState(user_id,user_input)
        # 1. 初始化消息上下文
        messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_input}]

        for turn in range(self.max_steps):
            response=self.llm.chat(messages,tools=TOOL_SCHEMAS)
            if not response:
                return self._finish(state, "LLM 响应异常任务已结束", "failed")

            if isinstance(response, Plan):
                self.manager.set_plan(response)
                self.manager.plan.status="running"

                # 记录 llm_decision
                state.add_trace("llm_decision",decision="plan_generated",steps=[
                    {"step_id": s.step_id,"task":s.task ,"depends_on":s.depends_on } for s in response.steps
                ])


                while(self.manager.get_ready_steps()):

                    steps=self.manager.get_ready_steps()
                    if not steps:
                        return self._finish(state, "LLM 无任务规划或者任务已完成直接结束")

                    for s in steps:
                        state.current_step=s.step_id
                        state.step_states[s.task]="running"
                        s.status = "running"
                        # 记录步骤更新
                        state.add_trace(
                            "step_update",
                            step_id=s.step_id,
                            task=s.task,
                            status="running"
                        )

                        executor=ToolExecutor(tools=self.tools)

                        # 第一次调用
                        state.add_trace(
                            "tool_execution",
                            step_id=s.step_id,
                            tool_name=s.task,
                            attempt=1,
                            status="running"
                        )
                        tool_result=executor.execute_tool(s.task,user_id,s.order_id)
                        #  第一次调用的结果
                        state.add_trace(
                            "tool_execution",
                            step_id=s.step_id,
                            tool_name=s.task,
                            attempt=1,
                            status="success" if tool_result.get("success") else "failed",
                            result=tool_result
                        )

                        if  tool_result.get("error") and "db timeout" in tool_result["error"]:
                            # 记录 tool_retry
                            state.add_trace(
                                "tool_retry",
                                step_id=s.step_id,
                                tool_name=s.task,
                                attempt=2,
                                reason="db_timeout"
                            )
                            # 技术异常可以重试
                            tool_result = executor.execute_tool(s.task, user_id, s.order_id)

                            state.add_trace(
                                "tool_execution",
                                step_id=s.step_id,
                                tool_name=s.task,
                                attempt=2,
                                status="success" if tool_result.get("success") else "failed",
                                result=tool_result
                            )


                        state.step_results[s.task]=tool_result
                        # 记录返回结果
                        state.add_trace("observation",step_id=s.step_id,tool_name=s.task, result=tool_result)
                        #  将 Observation 返回给 LLM
                        messages.append({
                            "role": "tool",
                            "name": s.task,
                            "content": json.dumps(
                                tool_result,
                                ensure_ascii=False
                            )
                        })
                        if not tool_result.get("success"):
                            state.step_states[s.task]="failed"
                            self.manager.mark_failed(s.step_id)
                            self.manager.plan.status="failed"
                            state.add_trace(
                                "step_update",
                                step_id=s.step_id,
                                task=s.task,
                                status="failed"
                            )
                            return self._finish(state, f"工具执行失败:{tool_result['error']}", "failed")

                        if s.task == "permission_check" and not tool_result.get("allowed"):
                            state.step_states[s.task] = "failed"
                            self.manager.mark_failed(s.step_id)
                            self.manager.plan.status = "failed"
                            state.add_trace(
                                "agent_decision",
                                action="stop",
                                reason="permission_denied",
                                step_id=s.step_id
                            )
                            return self._finish(state, f"权限校验失败:{tool_result['reason']}", "failed")

                        state.step_states[s.task] ="completed"
                        self.manager.mark_completed(s.step_id)

                        state.add_trace(
                            "step_update",
                            step_id=s.step_id,
                            task=s.task,
                            status="completed"
                        )


            else:
                self.manager.plan.status="completed"
                return self._finish(state, response.get("content"))



         #  达到最大调用次数
        return self._finish(state, "Error: Maximum tool calling steps reached", "failed")






