import json

from agent.llm_agent import LLMToolAgent
from agent.memory import ShortTermMemory, build_context
from agent.persistence import JsonPersistence
from agent.plan_manager import PlanManager
from agent.planning import Plan, Step
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


# 具有planning能力的Agent, 跟进LLM返回的plan来规划执行路径, 并加入了RAG 检索能力

class LLMPlanAgent(LLMToolAgent):
    def __init__(self, llm,tools,memory:ShortTermMemory=None,max_steps=5,max_tool_calls:int=5,persistence:JsonPersistence=None,retriever=None):
        self.manager = PlanManager(Plan()) # Agent的任务规划管理
        self.tools = tools                # agent 调用的Function calling
        self.max_steps = max_steps        # 最大对话执行轮数
        self.memory = memory              # 短期记忆，内存中
        self.persistence = persistence   #记忆存储，写入本地文档
        self.retriever = retriever      # RAG 检索功能
        super().__init__(llm,tools,max_steps,max_tool_calls)

    def resume(self,plan_id,task_id):

        plan=self.persistence.load_plan(plan_id) if self.persistence else None
        state=self.persistence.load_state(task_id) if self.persistence else None

        if plan is None:
            raise ValueError("Plan not found")

        self.manager.set_plan(plan)
        self.manager.plan.status = "running"
        messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT},{"role": "user", "content":plan.user_input }]
        state=self.execute_remaining_steps(plan.user_id,messages,state)
        if state.final_response:
            return state

        return state


    def execute_remaining_steps(self,user_id,messages,state):
        count=0
        while (self.manager.get_ready_steps() and count < self.max_tool_calls):
            steps = self.manager.get_ready_steps()
            count+=1
            if not steps:
                return self._finish(state, "LLM 无任务规划或者任务已完成直接结束")

            for s in steps:
                state.current_step = s.step_id
                state.step_states[s.task] = "running"
                s.status = "running"
                # 记录步骤更新
                state.add_trace(
                    "step_update",
                    step_id=s.step_id,
                    task=s.task,
                    status="running"
                )
                # 工具执行前保存 checkpoint
                self.persistence.save_checkpoint(self.manager.plan) if self.persistence else None
                self.persistence.save_checkpoint(state) if self.persistence else None

                executor = ToolExecutor(tools=self.tools)

                # 第一次调用
                state.add_trace(
                    "tool_execution",
                    step_id=s.step_id,
                    tool_name=s.task,
                    attempt=1,
                    status="running"
                )
                tool_result = executor.execute_tool(s.task, user_id, s.order_id)
                #  第一次调用的结果
                state.add_trace(
                    "tool_execution",
                    step_id=s.step_id,
                    tool_name=s.task,
                    attempt=1,
                    status="success" if tool_result.get("success") else "failed",
                    result=tool_result
                )

                if tool_result.get("error") and "db timeout" in tool_result["error"]:
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

                state.step_results[s.task] = tool_result
                # 记录返回结果
                state.add_trace("observation", step_id=s.step_id, tool_name=s.task, result=tool_result)
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
                    state.step_states[s.task] = "failed"
                    self.manager.mark_failed(s.step_id)
                    self.manager.plan.status = "failed"
                    state.add_trace(
                        "step_update",
                        step_id=s.step_id,
                        task=s.task,
                        status="failed"
                    )
                    # 更新步骤结果
                    self.manager.update_step_result(s.step_id, tool_result)
                    self.persistence.save_checkpoint(self.manager.plan) if self.persistence else None
                    self.persistence.save_checkpoint(state) if self.persistence else None
                    # memory 写回操作
                    if self.memory:
                        self.memory.update_context("previous_action", s.task)
                        self.memory.update_context("previous_result", "failed")
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
                    # 更新步骤结果
                    self.manager.update_step_result(s.step_id, tool_result)
                    self.persistence.save_checkpoint(self.manager.plan) if self.persistence else None
                    self.persistence.save_checkpoint(state) if self.persistence else None
                    # memory 写回操作
                    if self.memory:
                        self.memory.update_context("previous_action", s.task)
                        self.memory.update_context("previous_result", "failed")
                    return self._finish(state, f"权限校验失败:{tool_result['reason']}", "failed")

                state.step_states[s.task] = "completed"
                self.manager.mark_completed(s.step_id)

                # memory 写回操作
                if self.memory:
                    self.memory.update_context("previous_action", s.task)
                    self.memory.update_context("previous_result", "success")

                state.add_trace(
                    "step_update",
                    step_id=s.step_id,
                    task=s.task,
                    status="completed"
                )
                # 更新步骤结果
                self.manager.update_step_result(s.step_id, tool_result)
                self.persistence.save_checkpoint(self.manager.plan) if self.persistence else None
                self.persistence.save_checkpoint(state) if self.persistence else None

        for step in self.manager.plan.steps:
            if not step.status=="completed":
                self.manager.plan.status = "failed"
                return state
        self.manager.plan.status = "completed"

        return state


    def build_rag_context(self,docs):
        reference = "参考资料："

        for i, doc in enumerate(docs, start=1):
            reference += f"\n{i}. {doc}"

        return reference

    def run(self,user_id,user_input) -> AgentState:

        state=AgentState(user_id,user_input)
        # 1. 初始化消息上下文--加入系统prompt
        messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

        #  初始化消息上下文--加入history messages
        try:
            if self.memory:
                # 获取历史消息
                messages.extend(self.memory.messages) if self.memory.messages else None

                if self.memory.context:
                    # 过滤无关信息
                    context=build_context(self.memory,["user_id","order_id","previous_action","previous_result"])
                    messages.append({"role": "memory","content": context})
        except Exception:
            # Memory 异常时，不阻断 Agent 的基本执行
            pass

        # 如果有检索内容，把检索到的内容也加入用户输入中
        if self.retriever:
            # 获取RAG检索到的序号
            retrieve_num=self.retriever.retrieve(query=user_input,top_k=3)
            # 获取RAG检索到的序号对应的文本内容
            retriever_doc = [self.retriever.docs.get(x) for x in retrieve_num]

            # RAG检索到的参考内容
            reference=self.build_rag_context(retriever_doc)

            # 更新user_input,加入参考内容
            user_input=f"用户问题：{user_input}。{reference}"


        # 初始化消息上下文---加入用户输入
        messages.append({"role": "user", "content": user_input})

        # 2. 进行多轮对话
        for turn in range(self.max_steps):

            response=self.llm.chat(messages,tools=TOOL_SCHEMAS)

            if not response:
                return self._finish(state, "LLM 响应异常任务已结束", "failed")

            messages.append({"role": "assistant", "content": response})

            if isinstance(response, Plan):
                self.manager.set_plan(response)
                self.manager.plan.status="running"
                self.manager.plan.user_id=user_id
                self.manager.plan.user_input=user_input

                # 记录 llm_decision
                state.add_trace("llm_decision",decision="plan_generated",steps=[
                    {"step_id": s.step_id,"task":s.task ,"depends_on":s.depends_on } for s in response.steps
                ])

                #执行剩余步骤
                self.execute_remaining_steps(user_id,messages,state)

                if state.final_response:
                    return state


            else:
                state.status="completed"
                self.persistence.save_checkpoint(self.manager.plan) if self.persistence else None
                self.persistence.save_checkpoint(state) if self.persistence else None
                return self._finish(state, response.get("content"))



         #  达到最大调用次数
        return self._finish(state, "Error: Maximum tool calling steps reached", "failed")






