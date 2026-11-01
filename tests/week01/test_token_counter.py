import pytest

from src.utils.token_counter import TokenCounter

# 统计Token

@pytest.fixture(scope="function")
def counter():
    return TokenCounter()


@pytest.mark.parametrize("text",[ "Hello world",
    "我的订单已经支付成功",
     "124545342",
    "!@#$%^&*()",
    "Order A10086 payment status",
    "订单 A10086 支付状态：SUCCESS"])
def test_normal_text(counter, text    ):
    #检查英文文本，中文文本，数字文本，特殊字符，多语言混合场景下，返回长度为正整数
    size=counter.count(text)
    assert isinstance(size,int)
    assert size>0

def test_empty_text(counter ):
    #检查空字符串长度
    assert counter.count("")==0

def test_long_text(counter ):
    #检查长文本
    text="""观察不同文本的 Token 数量。
不要预先假设中文一定比英文消耗更多或更少 Token，要通过实际编码结果验证。
2.5 核心知识四：设计 Token 测试用例
今天不要只写一个正常场景。你需要考虑输入边界、数据类型和异常情况。""" *10000
    size=counter.count(text)
    assert size==950000

@pytest.mark.parametrize("text",[123,[],{},None])
def test_invalid_input(counter, text ):
    #检查非字符串
    with pytest.raises(TypeError,match="输入必须是字符串"):
        counter.count(text)

def test_token_count_is_consistent(counter):
    #验证统计结果稳定
    text = "订单 A10086 支付状态：SUCCESS"

    first = counter.count(text)
    second = counter.count(text)

    assert first == second