from agent.llm_agent_plan import LLMPlanAgent
from agent.planning import Step, Plan
from tests.conftest import FakeLLM
from utils.tool import text_response


def test_01_normal_trace(env):
    step1=Step(step_id="step01", task="query_order", order_id="ORD1001",depends_on=[])
    llm=FakeLLM([Plan(steps=[step1]),text_response("订单ORD1001查询成功")])

    agent=LLMPlanAgent(llm,env["tools"])

    state=agent.run("U001","查询订单ORD1001")

    assert agent.manager.plan.status=="completed"

    for step in agent.manager.plan.steps:
        assert step.status=="completed"

    assert state.step_states.get("query_order")=="completed"

    llm_decision = [event for event in state.trace if event["type"] == "llm_decision"]
    assert len(llm_decision) == 1
    assert llm_decision[0]["steps"]== [{'step_id': 'step01', 'task': 'query_order', 'depends_on': []}]
    #

    update=[event for event in state.trace if event["type"] == "step_update"]
    assert len(update)==2
    assert update[0]["status"]=="running"
    assert update[1]["status"] == "completed"

    execution = [event for event in state.trace if event["type"] == "tool_execution"]
    assert len(execution) == 2
    assert execution[0]["status"] == "running"
    assert execution[1]["status"] == "success"

    observation = [event for event in state.trace if event["type"] == "observation"]
    assert len(observation) == 1
    assert observation[0]["result"]["success"]==True

    final = [event for event in state.trace if event["type"] == "final_response"]
    assert len(final) == 1
    assert final[0]["content"] == "订单ORD1001查询成功" and final[0]["status"] == "success"

    event_types = [event["type"] for event in state.trace]
    assert event_types.index("llm_decision") < event_types.index("tool_execution")
    assert event_types.index("observation") < event_types.index("final_response")



def test_02_trace_when_permission_check_not_allowed(env):
    from unittest.mock import Mock
    execute_refund=env["tools"]["execute_refund"]
    execute_refund.execute_refund = Mock(wraps=execute_refund.execute_refund)

    step1=Step(step_id="step01", task="query_order", order_id="ORD1001",depends_on=[])
    step2 = Step(step_id="step02", task="permission_check", order_id="ORD1001",depends_on=["step01"])
    step3 = Step(step_id="step03", task="execute_refund", depends_on=["step02"], order_id="ORD1001")

    llm=FakeLLM([Plan(steps=[step1,step2,step3])])

    agent=LLMPlanAgent(llm,env["tools"])

    state=agent.run("U002","查询订单ORD1001")

    assert agent.manager.plan.status=="failed"

    assert step1.status=="completed"
    assert step2.status=="failed"
    assert "用户无权操作该订单" in state.final_response

    observation = [event for event in state.trace if event["type"] == "observation"]
    assert len(observation) == 2
    assert observation[1]["type"] == "observation"
    assert observation[1]["step_id"] == "step02"
    assert observation[1]["result"]["success"] == True
    assert observation[1]["result"]["allowed"] == False
    assert observation[1]["result"]["reason"] == "用户无权操作该订单"

    assert execute_refund.execute_refund.call_count==0
    assert agent.manager.plan.steps[2].status == "pending"





def test_03_trace_when_timeout_retry(env_timeout_retry_order_tool):
     """
    验证：trace能正常记录重试场景
     """
     from unittest.mock import Mock
     query_order = env_timeout_retry_order_tool["tools"]["query_order"]
     permission_check = env_timeout_retry_order_tool["tools"]["permission_check"]

     query_order.query_order = Mock(wraps=query_order.query_order)
     permission_check.check_permission = Mock(wraps=permission_check.check_permission)

     step1 = Step(step_id="step01", task="query_order", order_id="ORD1001")
     step2 = Step(step_id="step02", task="permission_check", depends_on=["step01"], order_id="ORD1001")
     llm = FakeLLM([Plan(steps=[step1, step2]), text_response("订单ORD1001查询成功")])

     agent = LLMPlanAgent(llm, env_timeout_retry_order_tool["tools"])
     state = agent.run("U001", "帮我查订单 ORD1001")

     assert state.step_states.get("query_order")=="completed"
     assert state.step_states.get("permission_check") == "completed"

     result=state.step_results.get("permission_check")
     assert result["success"]==True
     assert result["allowed"] == True
     assert result["reason"] == "用户有权操作该订单"

     assert query_order.query_order.call_count == 2
     assert permission_check.check_permission.call_count == 1


     tool_events=[event for event in state.trace if event["type"]=="tool_execution" and event["step_id"] == "step01"]

     assert len(tool_events) == 3
     assert tool_events[0]["attempt"] == 1
     assert tool_events[0]["status"] == "running"
     assert tool_events[1]["attempt"] == 1
     assert tool_events[1]["status"] == "failed"
     assert tool_events[2]["attempt"] == 2
     assert tool_events[2]["status"] == "success"


