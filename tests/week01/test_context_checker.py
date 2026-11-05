import pytest

from src.utils.context_checker import ContextChecker
from src.utils.token_counter import TokenCounter


#测试LLM的上下文窗口大小"


#用于模拟token计算的值
class FakeTokenCounter:
    def __init__(self, token_count):
        self.token_count = token_count

    def count(self, text):
        return self.token_count



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
#  使用FakeTokenCounter 来代替具体的文本，
# text="订单 A10086 支付状态：SUCCESS订单 A10086 支付状态：SUCCESS,A10086 支付状态：SUCCESS," # token=30
# text1="订单 A10086 支付状态：SUCCESS订单 A10086 支付状态：SUCCESS,A10086 支付状态：SUCCESS,ab" # token=31
# text2="订单 A10086 支付状态：SUCCESS订单 A10086 支付状态：SUCCESS"  # token=20
# text3= "订单 A10086 支付状态：SUCCESS订单 A10086 支付状态：SUCCESS.." # token=21


@pytest.mark.parametrize("inputToken,reserved",[(30,0),(20,10),(29,1),(1,29)])
def test_normal_context(inputToken,reserved):
    # 输入和输出预留总量刚好等于上限。inputToken+reserved=20+10=30 ,inputToken+reserved=30+0=30 等
    context=ContextChecker(FakeTokenCounter(inputToken),30)
    result=context.can_fit("订单查询",reserved)
    # print(result)
    assert isinstance(result,bool)
    assert result



@pytest.mark.parametrize("inputToken,reserved",[(30,1),(31,0),(21,10)])
def test_over_context(context,inputToken,reserved):
    # 输入和输出预留总量超过上限,30+1,31+0,21+10
    context = ContextChecker(FakeTokenCounter(inputToken), 30)
    result=context.can_fit("查询订单",reserved)

    assert isinstance(result,bool)
    assert not result

def test_empty_text_can_fit():
    checker = ContextChecker(FakeTokenCounter(0), 30)

    assert checker.can_fit("", 0) is True


@pytest.mark.parametrize("reserved",[-1])
def test_invalid_reserved_token(context,reserved):
    # 输出预留空间为 -1
    with pytest.raises(ValueError,match="reserved_tokens must be non-negative"):
        context.can_fit("查询订单",reserved)

@pytest.mark.parametrize("reserved",["abc",12.5,"10",{},None,True,False])
def test_invalid_type_reserved_token(context,reserved):
    # 输出预留空间为非整数类型
    with pytest.raises(TypeError,match="reserved_tokens must be integer"):
        context.can_fit("查询订单",reserved)




@pytest.mark.parametrize("text",[123,[],{}])
def test_invalid_input(context,text):
    # 输入为非文本类型，是其他类型,123,[],{}
    with pytest.raises(TypeError,match="输入必须是字符串"):
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