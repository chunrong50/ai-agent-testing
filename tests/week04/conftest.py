
documents = {
    "D001": "订单未发货前可以申请取消订单",
    "D002": "订单支付成功后，符合条件可以申请退款",
    "D003": "申请退款需要验证用户是否具有订单操作权限",
    "D004": "用户可以通过订单号查询支付状态",
}



# fake RAG检索工具
class FakeRetriever:
    def __init__(self,documents,args):
        self.docs = documents
        self.results = list(args)

    def add(self, doc_id, text):
        self.docs[doc_id] = text

    def update(self, doc_id, text):
        if doc_id not in self.docs:
            raise KeyError(doc_id)
        self.docs[doc_id] = text

    def delete(self, doc_id):
        self.docs.pop(doc_id, None)

    # def retrieve(self, query, top_k=3):
    #     # 简单规则：统计 query 中的词在文档里出现的数量
    #     keywords = [w for w in ["退款", "期限", "7天", "15天", "无理由","已支付"] if w in query]
    #     scored = []
    #     for doc_id, text in self.docs.items():
    #         score = sum(1 for w in keywords if w in text)
    #         if score > 0:
    #             scored.append((doc_id, score))
    #     scored.sort(key=lambda x: x[1], reverse=True)
    #     return [doc_id for doc_id, _ in scored[:top_k]]

    def retrieve(self,query,top_k=3):
        return self.results[:top_k]


class FakeReranker:
    def __init__(self,retrieve_result,args):
        self.retrieve_result = retrieve_result
        self.results = list(args)


    def rerank(self, query, top_k=3):
        return self.results[:top_k]






class FakeReranker2:
    # Claude AI
    def __init__(self, retrieve_result, relevance):
        self.retrieve_result = retrieve_result
        self.relevance = relevance   # {"D003": 0.9, "D005": 0.8, ...}

    def rerank(self, query, top_k=3):
        ranked = sorted(self.retrieve_result,
                        key=lambda d: self.relevance.get(d, 0),
                        reverse=True)
        return ranked[:top_k]