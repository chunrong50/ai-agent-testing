from agent.planning import Step, Plan


def test_01_refund_plan():
    step1=Step(step_id=1,task="query_order")
    step2=Step(step_id=2,task="permission_check",depends_on=[step1])
    step3 = Step(step_id=2, task="check_refund_eligibility", depends_on=[step2])
    step4 = Step(step_id=2, task="execute_refund", depends_on=[step3])

    plan=Plan(steps=[step1, step2, step3, step4])
    plan.task_plan()
    assert plan.status=="completed"
    assert step1.status=="completed"
    assert step2.status=="completed"
    assert step3.status=="completed"
    assert step4.status=="completed"
