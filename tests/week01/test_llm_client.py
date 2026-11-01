import pytest

from src.exceptions.llm_exceptions import LLMTimeoutError, LLMServerError
from src.llm.llm import FakeModel, EmptyModel, BlankModel, NotTextModel, TimeoutFakeModel, ServerErrorFakeModel, \
    SpyModel
from src.llm.llm_client import LLMClient


@pytest.fixture(scope="function")
def client():
    return LLMClient(FakeModel())



def test_normal_question(client):
    """TC001 测试场景：输入正常订单查询，模型正常处理"""
    result=client.ask("订单A10086支付成功了吗？")

    assert result=="订单支付成功"

@pytest.mark.parametrize(
    "question",
    ["", "   ", "\t", "\n",[],{},None]
)
def test_invalid_question(client, question):
    # TC002 测试场景：输入空字符串\空格、换行、tab， 预期：拒绝输入
    # TC003 测试场景：输入None， 预期：拒绝输入 。
    with pytest.raises(ValueError):
        client.ask(question)




def test_supper_long_question(client):
    # TC004 测试场景：输入超长文本， 预期：按长度策略处理
    result=client.ask("你是一个很爱学习的人，每天都在学习AI新知识，给你加油打气！看好你")
    assert result=="文本过长，请重新开一个窗口"


def test_empty_model_response():
    # TC005 测试场景：模型返回空结果， 预期：正确处理异常
    client=LLMClient(EmptyModel())
    with pytest.raises(ValueError):
        client.ask("查询订单")

def test_blank_model_response():
    # TC006 测试场景：模型返回空白， 预期：拒绝输入
    client = LLMClient(BlankModel())
    with pytest.raises(ValueError):  # 它包裹的代码块在执行时必须抛出 ValueError 异常，否则测试失败。测试要验证的就是"空输入会被拒绝"这个契约
        client.ask("查询订单")

def test_not_text_response():
    # TC007 测试场景：模型返回非字符串， 预期：正确处理类型异常
    client=LLMClient(NotTextModel())
    with pytest.raises(TypeError):
        client.ask("查询订单")




def test_model_timeout():
    # TC007 测试场景：模型接口超时， 预期：返回可识别错误
    """模型接口超时，应抛出可识别的 ModelTimeoutError"""
    client = LLMClient(TimeoutFakeModel(timeout_seconds=5))

    with pytest.raises(LLMTimeoutError, match="超时"):
        client.ask("查询订单")



def test_model_http_500():
    # TC008 测试场景：模型接口返回500， 预期：正确错误服务异常
    client = LLMClient(ServerErrorFakeModel())

    with pytest.raises(LLMServerError, match="500|服务"):
        client.ask("查询订单")


def test_question_passed_to_model():
    # TC009 验证 LLMClient把用户输入原样传给模型
    model = SpyModel()
    client = LLMClient(model)

    question = "订单A10086支付成功了吗？"

    client.ask(question)
    assert model.received_question == question
    assert "A10086" in model.received_question


# def test_model_get_question():
#     # TC0010 验证 LLMClient把用户输入传给模型，模型收到的输入与源数据不一致
#     model = SpyModel2()
#     client = LLMClient(model)
#
#     question = "订单A10086支付成功了吗？"
#
#     client.ask(question)
#     assert model.received_question != question