from src.exceptions.llm_exceptions import LLMServerError, LLMTimeoutError


class FakeModel:
    #  构造一个假模型，避免真实调用 LLM
    def generate(self,question):
        if len(question)<20:
            return "订单支付成功"
        else:
            return "文本过长，请重新开一个窗口"


class TimeoutFakeModel:
    """模拟调用即超时的假模型"""
    def __init__(self, timeout_seconds=30):
        self.timeout_seconds = timeout_seconds

    def generate(self, question):
        # 模拟底层 SDK 超时，例如 requests.Timeout / openai.APITimeoutError
        raise LLMTimeoutError(f"模型接口请求超时（>{self.timeout_seconds}s）")




class NotTextModel:
    def generate(self,question):
        return 12345

class EmptyModel:
    def generate(self,question):
        return ""

class BlankModel:
    def generate(self, question):
        return "   "


class ServerErrorFakeModel:
    #  构造一个假模型，模拟接口返回500
    def generate(self, question):
        raise LLMServerError(status_code=500)


class SpyModel:

    def __init__(self):
        self.received_question = None

    def generate(self, question):
        self.received_question = question
        return "查询完成"

class SpyModel2:

    def __init__(self):
        self.received_question = None

    def generate(self, question):
        #模型适配器收到的内容与用户不一致
        question=str.replace(question,"6","8")
        self.received_question = question
        print(f"模型收到的问题是：{self.received_question}")
        return "查询完成"