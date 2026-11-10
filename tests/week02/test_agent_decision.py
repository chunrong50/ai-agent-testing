from agent.planning import Step, Plan


def test_01_refund_plan():
    step1=Step(step_id="step01",task="query_order")
    step2=Step(step_id="step02",task="permission_check",depends_on=["step01"])
    step3 = Step(step_id="step03", task="check_refund_eligibility", depends_on=["step02"])
    step4 = Step(step_id="step04", task="execute_refund", depends_on=["step03"])

    plan=Plan(steps=[step1, step2, step3, step4])


    assert plan.status=="pending"
    assert step1.status=="pending"
    assert step2.status=="pending"
    assert step3.status=="pending"
    assert step4.status=="pending"
