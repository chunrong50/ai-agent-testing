from rag.evaluator import Evaluator
from tests.conftest import text_response
from tests.week04.conftest import documents, FakeRetriever


ground_truth = {
    "已支付订单如何申请退款": {
        "expected_docs": ["D002", "D003"]
    },
    "如何查询订单支付状态": {
        "expected_docs": ["D004"]
    },
    "未发货订单如何取消": {
        "expected_docs": ["D001"]
    }
}


def test_01_retrieval_all_expected():
    # Retriever 能否检索到正确文档
    retriever=FakeRetriever(documents,["D002","D004","D003"])
    query="已支付订单如何申请退款"
    actual=retriever.retrieve(query=query)
    assert actual==["D002","D004","D003"]

    expected=ground_truth.get(query).get("expected_docs")

    eval=Evaluator()
    assert eval.precision_at_k(actual,expected,3)==0.667
    assert eval.recall_at_k(actual, expected, 3) == 1.000


def test_02_context_passed_to_llm(agent_factory):
    # 检索文档能否完整传递给 LLM
    # 1. 准备文档
    doc=documents
    question = "已支付订单如何申请退款"

    # 2. 初始化 FakeRetriever RAG检索功能
    retriever = FakeRetriever(doc, ["D002", "D003"])

    responses=[text_response("订单 ORD1001 可以申请退款")]
    # 3. 初始化 FakeLLM, RAGAgent
    agent,llm,env=agent_factory(llm_responses=responses,retriever=retriever)

    # 4. 执行用户问题
    agent.run(user_id="U001",user_input=question)

    # 5. 获取 LLM 实际收到的 messages
    result=llm.calls[0]["message"][-1]["content"]

    # 7. 验证文档内容都传递给 LLM
    expected_num = ground_truth.get(question).get("expected_docs")

    expected_docs = [
        doc[x] for x in expected_num
    ]

    # 拼接期望结果
    reference = "参考资料："
    for i, doc in enumerate(expected_docs, start=1):
        reference += f"\n{i}. {doc}"

    assert reference in result


def test_03_rag_answer_faithfulness():
    pass