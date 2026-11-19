# 1.Evaluation Dataset
import pytest

evaluation_dataset = [
    {
        "name": "unpaid_order",
        "question": "为什么我的订单不能退款？",
        "context": {
            "order_id": "ORD1001",
            "status": "unpaid"
        },
        "expected_facts": [
            "未支付",
            "不能退款"
        ]
    },
    {
        "name": "paid_order",
        "question": "我的订单可以退款吗？",
        "context": {
            "order_id": "ORD1002",
            "status": "paid"
        },
        "expected_facts": [
            "已支付",
            "退款"
        ]
    },
    {
        "name": "missing_order",
        "question": "查询订单 ORD9999 的退款情况",
        "context": {
            "order_id": "ORD9999",
            "status": "not_found"
        },
        "expected_facts": [
            "未找到",
            "订单"
        ]
    }
]

#2. Evaluation 评估函数
def evaluate_response(response, expected_facts):
    """
    判断 LLM 输出是否包含必要的业务事实。
    返回：
    {
        "passed": True,
        "score": 1.0,
        "missing_facts": []
    }
    """
    if not expected_facts:
        raise ValueError("expected_facts cannot be empty")

    count=0
    missing_facts = []
    for expected_fact in expected_facts:
        if expected_fact in response:
            count += 1
        else:
            missing_facts.append(expected_fact)

    score = 1.0*count/len(expected_facts)
    passed= score== 1.0

    return {"passed": passed, "score": score, "missing_facts": missing_facts}


# 评估可靠性
def evaluate_reliability(
    agent,
    test_case,
    repeat=5
):
    results = []

    for _ in range(repeat):
        response = agent.run(test_case["input"])
        result = evaluate_response(
            response,
            test_case["expected"]
        )

        if result["passed"]:
            results.append(result)

    pass_count = len(results)

    return {
        "total": repeat,
        "passed": pass_count,
        "reliability": pass_count / repeat
    }


class Agent:
    def __init__(self, response):
        self.response = response
        self.calls=[]

    def run(self, input):
        self.calls.append(input)
        return self.response


@pytest.mark.parametrize("test_case", [{"input":"订单A10086未支付可以退款吗？","expected":["未支付","目前不能退款"]}])
def test_01_evaluation_reliability(test_case):
    response = "订单尚未支付，目前不能退款。"
    agent=Agent(response)
    result = evaluate_reliability(agent,test_case,repeat=5)
    assert result["passed"]==5
    assert result["reliability"]==1.0







def test_01_evaluation_correct_response():
    response = "订单尚未支付，目前不能退款。"

    result = evaluate_response(response,["未支付", "不能退款"])

    assert result["passed"] is True
    assert result["score"] == 1.0


def test_02_evaluation_incorrect_response():
    response = "订单已经支付，可以申请退款。"

    result = evaluate_response(response,["未支付", "不能退款"])

    assert result["passed"] is False
    assert result["score"] < 1.0
    assert result["missing_facts"] == ["未支付", "不能退款"]
