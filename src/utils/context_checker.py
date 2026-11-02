

class ContextChecker:
    #判断输入和预留输出是否超出上下文限制

    def __init__(self,token_counter,max_tokens):
        if type(max_tokens) is not int:
            raise TypeError("max_tokens must be an integer")
        if max_tokens <=0:
            raise ValueError("max_tokens must be positive")
        self.token_counter = token_counter
        self.max_tokens = max_tokens

    def can_fit(self,text:str,reserved_tokens=0):
        """输入 Token 数量 + 预留输出 Token 数量 不能超过最大上下文容量。"""
        if type(reserved_tokens) is not int :
            raise TypeError("reserved_tokens must be integer")

        if reserved_tokens < 0 :
            raise ValueError("reserved_tokens must be non-negative")


        input_tokens = self.token_counter.count(text)


        return input_tokens+reserved_tokens<=self.max_tokens