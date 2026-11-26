from decimal import Decimal,ROUND_HALF_UP


class Evaluator:


    def precision_at_k(self,retrieved_docs,expected_docs,k):
        # 计算前K个返回的检索准确率, 检索出来的文档中，有多少比例是真正相关的。
        top_k_docs=retrieved_docs[:k]

        count=sum([1 for doc in top_k_docs if doc in expected_docs])

        result=Decimal(count)/Decimal(k)

        return float(result.quantize(Decimal("0.001"),rounding=ROUND_HALF_UP))


    def recall_at_k(self,retrieved_docs,expected_docs,k):
        #计算前K检索召回率
        top_k_docs = retrieved_docs[:k]
        count = sum([1 for doc in top_k_docs if doc in expected_docs])

        result=Decimal(count)/Decimal(len(expected_docs))

        return float(result.quantize(Decimal("0.001"),rounding=ROUND_HALF_UP))



    def faithfulness(self, claims, supported_claims):
        # 计算得到 Context 支持的 Claim 比例
        if claims is None:
            return 0.0

        result = Decimal(len(supported_claims)) / Decimal(len(claims))

        return float(result.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP))




