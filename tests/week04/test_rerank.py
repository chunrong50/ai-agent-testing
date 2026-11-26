# 测试数据：
# retrieved_docs = ["D001", "D002", "D003", "D004", "D005"]
# reranked_docs = ["D003", "D005", "D002", "D001", "D004"]
# expected_top_docs = ["D003", "D005"]
#
# 你的任务：
# 编写一个 Pytest 测试，验证：
# 1. Reranker 接收 Retriever 返回的文档。
# 2. Reranker 输出重新排序后的文档。
# 3. 最相关的 D003、D005 位于前两名。
# 4. 原始文档没有丢失，也没有重复。
# 注意：测试要验证 Reranker 的排序结果，而不是直接断言一个手工构造的结果。
from tests.week04.conftest import FakeRetriever, FakeReranker, documents


def test_01_reranker():
    # 验证排序质量和结果完整性
    question = "已支付订单如何申请退款"
    relevant = {"D003", "D005"}

    # RAG 检索
    retriever = FakeRetriever(documents,["D001", "D002", "D003", "D004", "D005"])
    ret_result=retriever.retrieve(query=question,top_k=5)

    ## RAG 重排
    ranker = FakeReranker(ret_result,["D003", "D005", "D002", "D001", "D004"])
    rank_result=ranker.rerank(query=question,top_k=5)


    # 1. 相关文档都进入前 2 名（不锁定内部顺序）
    assert set(rank_result[:2]) == relevant

    # 2. 重排确实改变了顺序（排除"什么都没做"）
    assert rank_result != ret_result
    assert ret_result[0] not in relevant  # 重排前相关文档不在第一位

    # 3. 无丢失、无新增、无重复
    assert len(rank_result) == len(ret_result)
    assert set(rank_result) == set(ret_result)
    assert len(set(rank_result)) == len(rank_result)


def test_02_reranker_top_k():
    # 验证 Top-K 参数是否生效。
    question = "已支付订单如何申请退款"

    retriever = FakeRetriever(
        documents,
        ["D001", "D002", "D003", "D004", "D005"]
    )

    ret_result = retriever.retrieve(
        query=question,
        top_k=5
    )

    ranker = FakeReranker(
        ret_result,
        ["D003", "D005", "D002", "D001", "D004"]
    )

    rank_result = ranker.rerank(
        query=question,
        top_k=2
    )

    assert rank_result == ["D003", "D005"]
    assert len(rank_result) == 2