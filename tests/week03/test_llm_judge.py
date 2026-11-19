from tests.conftest import FakeJudge

#负责组织输入、调用 Judge
def evaluate_with_judge(
    judge_llm,
    business_rule,
    order_context,
    agent_response
    ):
    """
    将业务规则、订单事实和 Agent 回答发送给 Judge LLM。
    返回结构化评估结果。
    """
    return judge_llm.judge(business_rule,order_context,agent_response)


def test_judge_correct_response():
    business_rule = "未支付订单不能退款"

    order_context = {
        "status": "unpaid"
    }

    agent_response = "订单尚未支付，目前不能退款。"

    # 1. 创建 FakeJudge
    re={
    "passed": True,
    "score": 1.0,
    "reason": "回答符合业务规则"
    }
    judge_llm=FakeJudge(re)

    # 2. 调用 evaluate_with_judge()
    result=evaluate_with_judge(judge_llm,business_rule,order_context,agent_response)

    # 3. 验证 passed 和 score
    assert result["passed"] is True
    assert result["score"] == 1.0
    assert result["reason"] == "回答符合业务规则"




def test_judge_incorrect_response():
    from unittest.mock import Mock

    business_rule = "未支付订单不能退款"

    order_context = {
        "status": "unpaid"
    }

    agent_response = "订单尚未支付，目前可以退款。"

    # 1. 创建 FakeJudge
    re = {
        "passed": False,
        "score": 0.0,
        "reason": "回答违反业务规则"
    }
    judge_llm = FakeJudge(re)

    judge_llm.judge=Mock(wraps=judge_llm.judge)

    # 2. 调用 evaluate_with_judge()
    result = evaluate_with_judge(judge_llm, business_rule, order_context, agent_response)

    # 3. 验证 passed 和 score
    assert result["passed"] is False
    assert result["score"] <1.0
    assert result["reason"]=="回答违反业务规则"
    assert judge_llm.judge.call_count==1

    assert judge_llm.calls[0]["business_rule"]==business_rule
    assert judge_llm.calls[0]["order_context"] == order_context
    assert judge_llm.calls[0]["agent_response"] == agent_response