from agent.llm_agent_plan import LLMPlanAgent
from agent.persistence import JsonPersistence
from agent.planning import Step, Plan
from tests.conftest import FakeLLM
from utils.tool import text_response


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


    restore_plan = persistence.load_checkpoint("PLAN001")
    assert  restore_plan.status == "completed"
    assert restore_plan.plan_id == "PLAN001"

    assert len(restore_plan.steps) == 3
    assert restore_plan.steps[0].result["success"] is True

