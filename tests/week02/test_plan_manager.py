"""
今天先完成以下 5 个核心测试：
编号	测试场景	预期结果
T01	创建包含三个步骤的 Plan	Plan 保存成功
T02	所有步骤都是 pending	只允许执行 step1
T03	step1 完成	允许执行 step2
T04	step1、step2 完成	允许执行 step3
T05	step2 失败	不允许执行 step3
"""

from agent.plan_manager import PlanManager
from agent.planning import Step, Plan



def test_01_create_plan():
    step1=Step(step_id="step01",task="query_order")
    step2=Step(step_id="step02",task="permission_check",depends_on=["step01"])
    step3 =Step(step_id="step03", task="execute_refund", depends_on=["step02"])

    plan = Plan(steps=[step1, step2, step3])

    assert len(plan.steps)==3
    assert plan.steps[0].step_id == "step01"
    assert plan.steps[1].step_id == "step02"
    assert plan.steps[2].step_id == "step03"

    assert plan.steps[1].depends_on == ["step01"]
    assert plan.steps[2].depends_on == ["step02"]


def test_02_execute_step1_when_all_pending():
    step1=Step(step_id="step01",task="query_order")
    step2=Step(step_id="step02",task="permission_check",depends_on=["step01"])
    step3 =Step(step_id="step03", task="execute_refund", depends_on=["step02"])

    plan = Plan(steps=[step1, step2, step3])
    manager=PlanManager(plan)

    assert manager.get_ready_steps()==[step1]

#
def test_03_step1_completed_then_execute_step2():
    step1=Step(step_id="step01",task="query_order")
    step2=Step(step_id="step02",task="permission_check",depends_on=["step01"])
    step3 =Step(step_id="step03", task="execute_refund", depends_on=["step02"])

    plan = Plan(steps=[step1, step2, step3])
    manager=PlanManager(plan)

    manager.mark_completed(step_id="step01")
    assert manager.get_ready_steps()==[step2]
#
def test_04_step1_step2_completed_then_execute_step3():
    step1=Step(step_id="step01",task="query_order")
    step2=Step(step_id="step02",task="permission_check",depends_on=["step01"])
    step3 =Step(step_id="step03", task="execute_refund", depends_on=["step02"])

    plan = Plan(steps=[step1, step2, step3])
    manager=PlanManager(plan)

    manager.mark_completed(step_id="step01")
    manager.mark_completed(step_id="step02")

    assert manager.get_ready_steps()==[step3]
#
def test_05_step2_failed_then_not_execute_step3():
    step1=Step(step_id="step01",task="query_order")
    step2=Step(step_id="step02",task="permission_check",depends_on=["step01"])
    step3 =Step(step_id="step03", task="execute_refund", depends_on=["step02"])

    plan = Plan(steps=[step1, step2, step3])
    manager=PlanManager(plan)

    manager.mark_completed(step_id="step01")
    manager.mark_failed(step_id="step02")

    assert manager.get_ready_steps()==[]


def test_06_dependency_running_then_return_current_step():
    step1=Step(step_id="step01",task="query_order",status="running")
    step2=Step(step_id="step02",task="permission_check",depends_on=["step01"])
    step3 =Step(step_id="step03", task="execute_refund", depends_on=["step02"])

    plan = Plan(steps=[step1, step2, step3])
    manager=PlanManager(plan)

    assert manager.get_ready_steps()==[]


def test_07_plan_disorder():
    step1=Step(step_id="step01",task="query_order")
    step2=Step(step_id="step02",task="permission_check",depends_on=["step01"])
    step3 =Step(step_id="step03", task="execute_refund", depends_on=["step02"])

    plan = Plan(steps=[step3, step2, step1])
    manager=PlanManager(plan)
    assert manager.get_ready_steps()==[step1]

def test_08_steps_without_depends_on():
    step1=Step(step_id="step01",task="query_order")
    step2=Step(step_id="step02",task="permission_check")
    step3 = Step(step_id="step03", task="execute_refund", depends_on=["step02"])


    plan = Plan(steps=[step2, step1])
    manager=PlanManager(plan)
    # assert manager.get_ready_steps()==[step2, step1]


    plan2 = Plan(steps=[step1, step3, step2])
    manager.set_plan(plan2)
    assert manager.get_ready_steps() == [step1,step2]

def test_09_running_step_should_not_block_independent_steps():

    step1 = Step(
        step_id="step01",
        task="query_order"
    )

    step2 = Step(
        step_id="step02",
        task="permission_check",
        status="running"
    )

    step3 = Step(
        step_id="step03",
        task="send_notification"
    )

    plan = Plan(steps=[step1, step2, step3])
    manager = PlanManager(plan)

    assert manager.get_ready_steps() == [step1, step3]