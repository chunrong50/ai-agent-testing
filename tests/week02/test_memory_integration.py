#First version
# 测试编号	测试目标	预期结果
# TC01	历史记忆正确影响 Agent 决策	Agent 能读取相关历史信息
# TC02	Context 信息筛选正确	包含必要信息，排除无关信息
# TC03	Memory 读取异常	Agent 不应因此错误执行退款
# 其中 TC03 特别重要：Memory 服务不可用，不代表 Agent 可以跳过订单查询、权限验证和退款校验。


from agent.llm_agent_plan import LLMPlanAgent
from agent.memory import ShortTermMemory
from agent.planning import Plan, Step
from tests.conftest import FakeLLM, text_response


# Memory Injection
def test_day13_01_agent_retrieve_context(env):
    step1 = Step(step_id="step01", task="query_order", order_id="ORD1001")
    llm = FakeLLM([Plan(steps=[step1]), text_response("订单ORD1001查询成功")])

    memory=ShortTermMemory()
    memory.context={"user_id": "U001",
    "order_id": "ORD1001",
    "previous_action": "refund",
    "previous_result": "success",
    "unrelated_info": "用户喜欢红色商品"}
    agent=LLMPlanAgent(llm, env["tools"],memory=memory)

    state=agent.run("U001","帮我再次申请ORD1001的退款")

    msgs=[msg for msg in llm.calls[0].get("message") if msg["role"]=="memory"]

    assert msgs[0]["content"]["order_id"] == "ORD1001"
    assert msgs[0]["content"]["previous_action"] == "refund"
    assert "unrelated_info" not in msgs[0]["content"]

    assert state.step_results["query_order"]["success"]==True
    assert state.step_results["query_order"]["data"]["refund_status"]=="NOT_REFUNDED"


# Memory is None
def test_day13_02_agent_works_when_memory_is_None(env):
    step1 = Step(step_id="step01", task="query_order", order_id="ORD1001")
    llm = FakeLLM([Plan(steps=[step1]), text_response("订单ORD1001查询成功")])
    agent=LLMPlanAgent(llm, env["tools"])

    state=agent.run("U001","帮我查询订单ORD1001")
    assert agent.manager.plan.steps[0].status == "completed"
    assert agent.manager.plan.steps[0].step_id == "step01"

    assert agent.memory is None

    assert "订单ORD1001查询成功" in state.final_response


def test_day15_memory_writeback(env):
    step1 = Step(step_id="step01", task="query_order", order_id="ORD1001")
    llm = FakeLLM([Plan(steps=[step1]), text_response("订单ORD1001查询成功")])

    memory = ShortTermMemory()
    memory.context = {"user_id": "U001",
                      "order_id": "ORD1001",
                      "previous_action": "refund",
                      "previous_result": "failed",
                      "unrelated_info": "用户喜欢红色商品"}
    agent = LLMPlanAgent(llm, env["tools"], memory=memory)

    state = agent.run("U001", "帮我再次申请ORD1001的退款")

    assert agent.memory.retrieve_context("previous_action")=="query_order"
    assert agent.memory.retrieve_context("previous_result") == "success"

