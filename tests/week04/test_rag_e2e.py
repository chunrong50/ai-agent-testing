# 完整 RAG 流程
from rag.evaluator import Evaluator
from tests.conftest import text_response
from tests.week04.conftest import documents, FakeRetriever


def test_03_rag_answer_faithfulness(agent_factory):
    # 1. 准备 Retriever
    docs=documents
    question = "已支付订单如何申请退款"
    retriever = FakeRetriever(docs, ["D002","D004", "D003"])

    # 2. 准备 FakeLLM Response
    answer = """
    已支付订单可以申请退款。
    退款前必须验证订单归属。
    退款金额最高为5000元，必须在支付后7天内申请。
    """
    responses = [text_response(answer)]

    # 3. 初始化 Agent
    agent,llm,env = agent_factory(llm_responses=responses,retriever=retriever)


    # 4. 执行 agent.run()
    state=agent.run(user_id="U001",user_input=question)

    # 5. 获取最终 Answer
    final_answer=state.final_response

    # 6. 拆分 Claims
    claims=final_answer.strip().split("\n")
    new_claims=[]
    for claim in claims:
        if claim==" " or claim=='' or len(claim)<3:
            continue
        if "，" in  claim:
            claim_n=claim.split("，")
            for c in claim_n:
                new_claims.append(c)
        else:
            new_claims.append(claim)


    # 7. 根据 Context 标注 supported_claims
    supported_claims = [
        "已支付订单可以申请退款。",
        "退款前必须验证订单归属。"
    ]

    # 8. 调用 Evaluator
    eval=Evaluator()
    result=eval.faithfulness(new_claims,supported_claims)

    # 9. 验证 Faithfulness == 0.5
    assert result == 0.50

