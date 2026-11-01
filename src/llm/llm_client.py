class LLMClient:
    def __init__(self,model_adapter):
        self.model_adapter = model_adapter

    def ask(self,question:str) -> str:
        if question is None or len(question)==0:
            raise ValueError("问题不能为None,{},[]")

        if not question.strip():
            raise ValueError("问题不能为空")

        #你的 FakeModel 必须实现 generate方法
        result=self.model_adapter.generate(question)

        if not isinstance(result,str):
            raise TypeError("模型返回结果必须是字符串")

        if not result.strip():
            raise ValueError("模型返回内容不能为空")

        return result