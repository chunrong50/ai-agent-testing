from agent.llm_agent_plan import LLMPlanAgent
from agent.persistence import JsonPersistence
from agent.planning import Step, Plan
from tests.conftest import FakeLLM,text_response


def test_day17_01_checkpoint_persistence(env):

    step1=Step(step_id="step01",task="query_order",order_id="ORD1001")
    step2 = Step(step_id="step02", task="permission_check", order_id="ORD1001",depends_on=["step01"])
    step3 = Step(step_id="step03", task="execute_refund", order_id="ORD1001",depends_on=["step02"])
    llm = FakeLLM([Plan(steps=[step1,step2,step3],plan_id="PLAN001"),text_response("订单 ORD1001 退款成功")])
     # 持久化checkpoint
    persistence=JsonPersistence()
    agent = LLMPlanAgent(llm, env["tools"],persistence=persistence)
    state = agent.run("U001", "帮我查一下订单 ORD1001并退款")

    assert agent.manager.plan.status == "completed"

    restore_plan = persistence.load_plan("PLAN001")
    assert  restore_plan.status == "completed"
    assert restore_plan.plan_id == "PLAN001"

    assert len(restore_plan.steps) == 3
    assert restore_plan.steps[0].result["success"] is True


def test_day17_02_agent_resume(env):

    from unittest.mock import Mock
    query_order=env["tools"]["query_order"]
    permission_tool=env["tools"]["permission_check"]
    refund_tool = env["tools"]["execute_refund"]
    query_order.query_order = Mock(wraps=query_order.query_order)
    permission_tool.check_permission = Mock(wraps=permission_tool.check_permission)
    refund_tool.execute_refund = Mock(wraps=refund_tool.execute_refund)


    step1=Step(step_id="step01",task="query_order",order_id="ORD1001")
    step2 = Step(step_id="step02", task="permission_check", order_id="ORD1001",depends_on=["step01"])
    step3 = Step(step_id="step03", task="execute_refund", order_id="ORD1001",depends_on=["step02"])

    plan_id="PLAN001"
    llm = FakeLLM([Plan(steps=[step1,step2,step3],plan_id=plan_id),text_response("订单 ORD1001 退款成功")])

     # 持久化checkpoint
    persistence=JsonPersistence()
    # max_tool_calls=2, 使Step3 本次不能执行
    agent = LLMPlanAgent(llm, env["tools"],persistence=persistence,max_tool_calls=2)
    state = agent.run("U001", "帮我查一下订单 ORD1001并退款")
    task_id=state.task_id

    assert agent.manager.plan.status == "failed"
    assert agent.manager.plan.steps[0].status == "completed"
    assert agent.manager.plan.steps[1].status == "completed"
    assert agent.manager.plan.steps[2].status=="pending"

    # 模拟agent 重启后，开始执行step3
    agent2 = LLMPlanAgent(llm, env["tools"], persistence=persistence)
    state2=agent2.resume(plan_id,task_id)

    assert agent2.manager.plan.status == "completed"
    assert agent2.manager.plan.steps[0].status == "completed"
    assert agent2.manager.plan.steps[1].status == "completed"
    assert agent2.manager.plan.steps[2].status=="completed"

    assert query_order.query_order.call_count==1
    assert permission_tool.check_permission.call_count==1
    assert refund_tool.execute_refund.call_count == 1


