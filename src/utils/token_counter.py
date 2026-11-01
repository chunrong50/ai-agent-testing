import tiktoken


class TokenCounter:
    #统计文本 Token 数量
    def __init__(self,encoding_name="cl100k_base"):
        """cl100k_base 是一个具体的 Tokenizer 编码配置。实际项目中应优先使用目标模型官方指定的 Tokenizer；
        不能假设所有模型都使用同一编码"""
        self.encoding= tiktoken.get_encoding(encoding_name)

    def count(self,text) -> int:

        if not isinstance(text,str):
            raise TypeError("输入必须是字符串")

        if not text:
            return 0

        result=len(self.encoding.encode(text))
        # print(f"长度为：{result}")
        return result