from agent.llm_agent_plan import LLMPlanAgent
from agent.planning import Step, Plan
from tests.conftest import FakeLLM
from tests.week01.test_tool_calling_ai import text_resp
from utils.tool import text_response


def test_01_normal_trace(env):
    step1=Step(step_id="step01", task="query_order", order_id="ORD1001",depends_on=[])
    # step2 = Step(step_id="step02", task="permission_check", order_id="ORD1001")
    # step3 = Step(step_id="step03", task="execute_refund", order_id="ORD1001")
    llm=FakeLLM([Plan(steps=[step1]),text_response("订单ORD1001查询成功")])

    agent=LLMPlanAgent(llm,env["tools"])

    state=agent.run("U001","查询订单ORD1001")

    assert agent.manager.plan.status=="completed"

    for step in agent.manager.plan.steps:
        assert step.status=="completed"

    assert state.step_states.get("query_order")=="completed"

    assert state.trace[0]["type"]=="llm_decision"
    assert state.trace[0]["steps"]== [{'step_id': 'step01', 'task': 'query_order', 'depends_on': []}]
    #
    trace1= state.trace[1]
    assert trace1["type"]=="step_update" and trace1["step_id"]==step1.step_id  and trace1["status"]=="running"

    trace2= state.trace[2]
    assert trace2["type"] == "tool_execution" and trace2["step_id"] == step1.step_id
    assert trace2["attempt"]==1 and trace2["status"]=="running"
    #
    trace3= state.trace[3]
    assert trace3["type"] == "tool_execution" and trace3["step_id"] == step1.step_id
    assert trace3["attempt"]==1 and trace3["status"]=="success" and trace3["result"]["success"]==True

    #
    trace4 = state.trace[4]
    assert trace4["type"] == "observation" and trace4["step_id"] == step1.step_id and trace4["result"]["success"]==True

    trace5 = state.trace[5]
    assert trace5["type"] == "step_update" and trace5["step_id"] == step1.step_id and trace5["status"] == "completed"
    #
    trace6 = state.trace[6]
    assert trace6["type"] == "final_response" and trace6["content"] == "订单ORD1001查询成功" and trace6["status"] == "success"



def test_02_trace_when_permission_check_not_allowed(env):
    step1=Step(step_id="step01", task="query_order", order_id="ORD1001",depends_on=[])
    step2 = Step(step_id="step02", task="permission_check", order_id="ORD1001")

    llm=FakeLLM([Plan(steps=[step1,step2])])

    agent=LLMPlanAgent(llm,env["tools"])

    state=agent.run("U002","查询订单ORD1001")

    assert agent.manager.plan.status=="failed"

    assert step1.status=="completed"
    assert step2.status=="failed"
    assert "用户无权操作该订单" in state.final_response

    trace=state.trace[9]
    assert trace["type"] == "observation"
    assert trace["step_id"] == "step02"
    assert trace["result"]["success"] == True
    assert trace["result"]["allowed"] == False
    assert trace["result"]["reason"] == "用户无权操作该订单"



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

     assert query_order.query_order.call_count == 2
     assert permission_check.check_permission.call_count == 1

     trace_3=state.trace[3]
     assert trace_3["type"] == "tool_execution" and trace_3["step_id"] == "step01" and trace_3["attempt"]==1 and trace_3["status"]=="failed"

     trace_4 = state.trace[4]
     assert trace_4["type"] == "tool_retry" and trace_4["step_id"] == "step01" and trace_4["attempt"] == 2 and \
            trace_4["reason"] == "db_timeout"

     trace_5 = state.trace[5]
     assert trace_5["type"] == "tool_execution" and trace_5["step_id"] == "step01" and trace_5["attempt"] == 2 and \
            trace_5["status"] == "success"