import pytest

from src.utils.context_checker import ContextChecker
from src.utils.token_counter import TokenCounter

#测试LLM的上下文窗口大小"


@pytest.fixture(scope="function")
def context():
    return ContextChecker(TokenCounter(),30)

"""
cases: 
输入 Token 数量刚好达到上限。
输入 Token 数量比上限多 1。
输出预留空间为 0。
输入为空。
输入和输出预留总量刚好等于上限。
输入和输出预留总量超过上限 1。
reserved_tokens 为负数。
max_tokens 为 0 或负数。
"""

text="订单 A10086 支付状态：SUCCESS订单 A10086 支付状态：SUCCESS,A10086 支付状态：SUCCESS," # token=30
text1="订单 A10086 支付状态：SUCCESS订单 A10086 支付状态：SUCCESS,A10086 支付状态：SUCCESS,ab" # token=31
@pytest.mark.parametrize("text",[text,text1])
def test_input_token_equals_max(context,text):
    # 输入 Token 数量刚好达到上限/ 比上限多1。max=30
    result=context.can_fit(text,10)
    # print(result)
    assert isinstance(result,bool)
    assert not result


def test_normal_token(context):
    # 输入和输出预留总量刚好等于上限。text:20+reserved 10=30
    text="订单 A10086 支付状态：SUCCESS订单 A10086 支付状态：SUCCESS"
    result=context.can_fit(text,10)
    # print(result)

    assert isinstance(result,bool)
    assert result

def test_input_over_token(context):
    # 输入和输出预留总量超过上限 1
    text="订单 A10086 支付状态：SUCCESS订单 A10086 支付状态：SUCCESS.."
    result=context.can_fit(text,10)
    # print(result)

    assert isinstance(result,bool)
    assert not result


@pytest.mark.parametrize("reserved",[-1])
def test_reserved_token(context,reserved):
    # 输出预留空间为 0
    text="订单 A10086 支付状态：SUCCESS订单 A10086 支付状态：SUCCESS"

    with pytest.raises(ValueError,match="reserved_tokens must be positive"):
        context.can_fit(text,reserved)


@pytest.mark.parametrize("text",[123])
def test_invalid_input(context,text):
    # 输入为其他类型
    with pytest.raises(TypeError,match="输入必须是字符串"):
        context.can_fit(text,10)

@pytest.mark.parametrize("text",[[],{}])
def test_empty_input(context,text):
    # 输入为[],{}
    with pytest.raises(TypeError):
        context.can_fit(text,10)


def test_invalid_max_tokens():
    # 最大 Token 数为 0
    with pytest.raises(ValueError,match="max_tokens must be positive"):
        ContextChecker(TokenCounter(), 0)

@pytest.mark.parametrize("max_tokens",[30.5,True,"abc"])
def test_type_error_max_tokens(max_tokens):
    # 最大 Token 数为非整数
    with pytest.raises(TypeError,match="max_tokens must be an integer"):
        ContextChecker(TokenCounter(), max_tokens)