from agent.planning import Plan, Step


def test_01_step_failed_and_break_next_step_run(agent_factory):
    # 订单不存在，会终止后续step的执行


    step1 = Step(step_id="step01", task="query_order", order_id="ORD1008")
    step2 = Step(step_id="step02", task="permission_check", order_id="ORD1008")
    responses=[Plan(steps=[step1,step2])]

    agent,llm,env = agent_factory(llm_responses=responses)

    from unittest.mock import Mock
    query_order = env["tools"]["query_order"]
    permission_check = env["tools"]["permission_check"]
    query_order.query_order = Mock(wraps=query_order.query_order)
    permission_check.check_permission = Mock(wraps=permission_check.check_permission)

    state = agent.run("U001", "帮我查一下订单 ORD1008")

    assert state.step_states.get("query_order") == "failed"
    assert state.step_results["query_order"]["success"] == False
    assert agent.manager.plan.steps[0].status == "failed"
    assert agent.manager.plan.steps[1].status == "pending"

    assert query_order.query_order.call_count==1
    assert permission_check.check_permission.call_count==0