from agent.llm_agent_plan import LLMPlanAgent
from agent.planning import Step, Plan
from tests.conftest import FakeLLM


# Day 14
def test_01_step_failure_preserves_completed_steps(env):
    from unittest.mock import Mock

    # 1. 获取退款工具
    refund_tool= env["tools"]["execute_refund"]

    # 使用 Mock 模拟退款异常
    refund_tool.execute_refund=Mock(side_effect=RuntimeError("refund service error"))

    # 2. 创建三个 Step
    step1 = Step(
        step_id="step01",
        task="query_order",
        order_id="ORD1001"
    )

    # 创建 step2 permission_check
    # 依赖 step01
    step2 = Step(
        step_id="step02",
        task="permission_check",
        order_id="ORD1001",
        depends_on=["step01"]
    )

    # 创建 step3 execute_refund
    # 依赖 step02
    step3 = Step(
        step_id="step03",
        task="execute_refund",
        order_id="ORD1001",
        depends_on=["step02"]
    )

    # 3. 创建 Plan
    plan=Plan(steps=[step1,step2,step3])

    # 4. 创建 FakeLLM
    llm=FakeLLM([plan])


    # 5. 创建 Agent 并执行
    agent=LLMPlanAgent(llm,tools=env["tools"])
    state=agent.run("U001","查询订单ORD1001并退款")


    # 6. 验证执行结果
    #  验证 Step 1 completed ,Step 2 completed ,Step 3 failed
    assert state.step_states["query_order"]=="completed"
    assert state.step_states["permission_check"] == "completed"
    assert state.step_states["execute_refund"] == "failed"

    # 7. 验证 Plan 状态
    #  Plan 应该 failed
    assert agent.manager.plan.status=="failed"
    assert agent.manager.plan.steps[0].status=="completed"
    assert agent.manager.plan.steps[1].status == "completed"
    assert agent.manager.plan.steps[2].status == "failed"

    # 8.退款工具只调用了1次
    assert refund_tool.execute_refund.call_count==1
