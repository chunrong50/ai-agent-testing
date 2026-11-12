from agent.llm_agent_plan import LLMPlanAgent
from agent.planning import Step, Plan
from tests.conftest import FakeLLM
from utils.tool import text_response

'''
Day 9 保留以下 5 个测试：
编号	测试场景	核心验证
TC01	Step 执行成功	     状态是否正确更新为 completed
TC02	Step 执行失败 	  是否正确记录 failed，阻止不应执行的后续步骤
TC03	已完成 Step 恢复执行	 是否避免重复执行
TC04	技术异常发生	是否正确记录异常并处理执行状态
TC05	业务校验失败	是否终止后续退款和通知步骤
'''




def test_01_step_success_and_status_should_be_completed(env):
    step1=Step(step_id="step01",task="query_order",order_id="ORD1001")
    llm = FakeLLM([Plan(steps=[step1]),text_response("订单 ORD1001 查询成功，订单已支付199.00")])
    agent = LLMPlanAgent(llm, env["tools"])
    state = agent.run("U001", "帮我查一下订单 ORD1001")

    assert state.step_states.get("query_order")=="completed"
    assert state.step_results["query_order"]["success"]==True
    assert agent.manager.plan.steps[0].status == "completed"

    assert "订单已支付199.00" in state.final_response



def test_02_step_failed_and_break_next_step_run(env):
    # 订单不存在，会终止后续step的执行
    step1 = Step(step_id="step01", task="query_order", order_id="ORD1008")
    step2 = Step(step_id="step02", task="permission_check", order_id="ORD1008")
    llm = FakeLLM([Plan(steps=[step1,step2])])
    agent = LLMPlanAgent(llm, env["tools"])
    state = agent.run("U001", "帮我查一下订单 ORD1008")

    assert state.step_states.get("query_order") == "failed"
    assert state.step_results["query_order"]["success"] == False
    assert agent.manager.plan.steps[0].status == "failed"
    assert agent.manager.plan.steps[1].status == "pending"



def test_03_completed_step_should_not_execute_again(env):
    """
    验证：已经完成的步骤，在 Agent 恢复执行时不应该重复执行。
    """
    step1 = Step(step_id="step01", task="query_order", status="completed",order_id="ORD1001")
    step2 = Step(step_id="step02", task="permission_check", depends_on=["step01"],order_id="ORD1001")


    llm = FakeLLM([Plan(steps=[step1, step2]),text_response("订单 ORD1001 查询成功，订单已支付199.00")])
    agent = LLMPlanAgent(llm, env["tools"])
    state = agent.run("U001", "帮我查订单 ORD1001")

    assert state.step_states.get("query_order") is None
    assert state.step_states.get("permission_check") == "completed"

    assert state.step_results.get("query_order") is None
    assert state.step_results["permission_check"]["success"] == True
    assert agent.manager.plan.steps[0].status == "completed"
    assert agent.manager.plan.steps[1].status == "completed"



def test_04_failed_step_should_trigger_recovery_decision(env_timeout_order_tool):
     """
    验证：
     某个步骤执行失败后，Agent 应该根据失败原因
     决定重试、终止还是重新规划。 技术异常发生是否正确记录异常并处理执行状态
     """
     from unittest.mock import Mock
     query_order = env_timeout_order_tool["tools"]["query_order"]
     permission_check = env_timeout_order_tool["tools"]["permission_check"]

     query_order.query_order = Mock(wraps=query_order.query_order)
     permission_check.check_permission = Mock(wraps=permission_check.check_permission)

     step1 = Step(step_id="step01", task="query_order", order_id="ORD1001")
     step2 = Step(step_id="step02", task="permission_check", depends_on=["step01"], order_id="ORD1001")
     llm = FakeLLM([Plan(steps=[step1, step2]), text_response("订单ORD1001查询成功")])

     agent = LLMPlanAgent(llm, env_timeout_order_tool["tools"])
     state = agent.run("U001", "帮我查订单 ORD1001")

     assert state.step_states.get("query_order")=="failed"
     assert "db timeout" in state.step_results["query_order"]["error"]

     assert agent.manager.plan.steps[1].status == "pending"

     assert query_order.query_order.call_count==2
     assert permission_check.check_permission.call_count==0



def test_05_step_failed_due_to_business_check_and_finish(env):
    # TC05	业务校验失败	是否终止后续退款和通知步骤
    step1 = Step(step_id="step01", task="query_order",order_id="ORD1001")
    step2 = Step(step_id="step02", task="permission_check", depends_on=["step01"],order_id="ORD1001")
    step3 = Step(step_id="step03", task="refund_execute", depends_on=["step02"], order_id="ORD1001")

    llm = FakeLLM([Plan(steps=[step1, step2, step3])])
    agent = LLMPlanAgent(llm, env["tools"])
    #U002 没有操作ORD1001的权限
    state = agent.run("U002", "帮我把订单ORD1001退款")

    assert state.step_states.get("query_order")=="completed"
    assert state.step_states.get("permission_check") == "failed"
    assert state.step_results["query_order"]["success"]==True
    assert state.step_results["permission_check"]["success"] == True
    assert state.step_results["permission_check"]["allowed"]==False


    assert agent.manager.plan.steps[0].status == "completed"
    assert agent.manager.plan.steps[1].status == "failed"
    assert agent.manager.plan.steps[2].status == "pending"









