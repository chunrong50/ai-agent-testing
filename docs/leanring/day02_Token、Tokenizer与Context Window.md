 ---------------Day 2 课程——Token、Tokenizer 与 Context Window--------------

Week 1 · Day 2
理论 + 编码 + 自动化测试

理解 LLM 的输入边界与上下文限制
今天我们重点解决一个问题：

为什么 Agent 明明拿到了完整的用户问题和历史对话，却仍然可能遗漏关键信息？

这不仅是模型能力问题，也可能是 Token 计算、上下文窗口和输入截断导致的。
2.1 今天的学习目标
完成今天课程后，你应该能够：
1. 解释 Token、Tokenizer 和 Context Window 的关系。
2. 使用 Python 统计文本 Token 数量。
3. 理解中英文、数字、特殊字符的 Token 差异。
4. 设计上下文窗口边界测试。
5. 使用 Pytest 自动化验证 Token 统计和边界处理。
2.2 核心知识一：什么是 Token？
Token 是大语言模型处理文本时使用的基本单位。

它不完全等于一个汉字、一个英文单词或一个字符。

例如：
Hello, world!

可能被拆分为：
Hello
,
 world
!

中文：
我的订单已经支付成功

也可能被拆分成多个 Token，具体取决于模型使用的 Tokenizer。

需要记住：
- 一个英文单词可能是一个或多个 Token。
- 一个汉字可能是一个或多个 Token。
- 标点符号、空格、数字也会影响 Token 数量。
- 不同模型可能使用不同的 Tokenizer。
测试工程师需要关注什么？

假设用户输入：
请查询订单 A10086 的支付状态。

如果系统错误地估算 Token 数量，就可能导致：
- Prompt 超出模型上下文窗口。
- 历史消息被错误截断。
- 用户的关键订单信息丢失。
- Agent 无法正确调用订单查询工具。
2.3 核心知识二：什么是 Context Window？
Context Window（上下文窗口）指模型一次请求能够处理的上下文容量。

它通常包含：
- System Prompt
- Developer 指令
- User 输入
- 历史对话
- 工具调用及工具返回内容
- 模型生成的输出空间
例如，假设某模型的上下文窗口为 8,000 Tokens：
上下文窗口示意
System Prompt 1,000 Tokens

历史对话  3,000 Tokens

当前输入和工具结果  2,000 Tokens

预留输出空间 2,000 Tokens

总计
8,000

这是教学用的假设示例，不代表任何特定模型的实际配置。

测试重点：

输入 Token 数量没有超过上下文窗口，不代表请求一定能够成功。

还要考虑模型输出预留空间、工具调用内容、系统限制，以及服务端可能存在的额外约束。
2.4 核心知识三：如何使用 Python 统计 Token？
今天使用 tiktoken 进行实践。

安装：
pip install tiktoken

创建文件：
src/
└── utils/
    └── token_counter.py

实现 Token 统计工具：
import tiktoken


class TokenCounter:

    def __init__(self, encoding_name="cl100k_base"):
        self.encoding = tiktoken.get_encoding(
            encoding_name
        )

    def count(self, text: str) -> int:
        if not isinstance(text, str):
            raise TypeError("输入必须是字符串")

        if not text:
            return 0

        tokens = self.encoding.encode(text)

        return len(tokens)

注意：cl100k_base 是一个具体的 Tokenizer 编码配置。实际项目中应优先使用目标模型官方指定的 Tokenizer；不能假设所有模型都使用同一编码。

运行：
from src.utils.token_counter import TokenCounter

counter = TokenCounter()

texts = [
    "Hello world",
    "我的订单已经支付成功",
    "Order A10086 payment status",
    "订单 A10086 支付状态：SUCCESS"
]

for text in texts:
    print(text, counter.count(text))

观察不同文本的 Token 数量。

不要预先假设中文一定比英文消耗更多或更少 Token，要通过实际编码结果验证。
2.5 核心知识四：设计 Token 测试用例
今天不要只写一个正常场景。你需要考虑输入边界、数据类型和异常情况。
用例编号	测试场景	输入	预期结果
TC001	英文文本	Hello world	返回正整数
TC002	中文文本	订单支付成功	返回正整数
TC003	空字符串	""	返回 0
TC004	数字文本	123456789	返回正整数
TC005	特殊字符	!@#$%^&*()	返回正整数
TC006	长文本	重复生成大量字符	能正确统计
TC007	非字符串	123	抛出 TypeError
TC008	多语言混合	中英文、数字和符号	返回正整数

2.6 编码实战：使用 Pytest 自动化测试
创建：
tests/
└── week01/
    └── test_token_counter.py

参考代码：
import pytest

from src.utils.token_counter import TokenCounter


@pytest.fixture
def counter():
    return TokenCounter()


@pytest.mark.parametrize(
    "text",
    [
        "Hello world",
        "我的订单已经支付成功",
        "123456789",
        "!@#$%^&*()",
        "订单 A10086 payment SUCCESS",
    ]
)
def test_normal_text(counter, text):
    result = counter.count(text)

    assert isinstance(result, int)
    assert result > 0


def test_empty_text(counter):
    assert counter.count("") == 0


def test_long_text(counter):
    text = "订单支付成功" * 10000

    result = counter.count(text)

    assert result > 0


def test_invalid_input(counter):
    with pytest.raises(TypeError):
        counter.count(123)

执行：
pytest -v tests/week01/test_token_counter.py


第三部分：Day 2 进阶测试任务
这部分是今天最重要的内容。

你不只是要统计 Token，还要像测试真实 Agent 一样验证上下文窗口的处理能力。
任务一：实现上下文窗口检查器
创建：
src/utils/context_checker.py

要求实现：
class ContextChecker:

    def __init__(self, token_counter, max_tokens):
        pass

    def can_fit(self, text: str, reserved_tokens=0) -> bool:
        pass

业务规则：
输入 Token 数量 + 预留输出 Token 数量
不能超过最大上下文容量。

例如：
最大上下文	输入 Token	输出预留	预期
8000	3000	2000	True
8000	6000	2000	True
8000	6001	2000	False
8000	8000	100	False
8000	0	8000	True

注意：这里使用的是教学简化模型，实际 Agent 还要考虑其他消息、工具定义和服务端限制。
任务二：设计边界测试
至少覆盖：
- 输入 Token 数量刚好达到上限。
- 输入 Token 数量比上限多 1。
- 输出预留空间为 0。
- 输入为空。
- 输入和输出预留总量刚好等于上限。
- 输入和输出预留总量超过上限 1。
- reserved_tokens 为负数。
- max_tokens 为 0 或负数。
请自行决定非法参数应该抛出什么异常，并在测试报告中说明设计理由。
任务三：设计真实电商 Agent 测试场景
假设用户连续对 Agent 说：
第一轮：我的订单号是 A10086。

第二轮：帮我查一下支付状态。

第三轮：如果已经支付成功，帮我确认能不能申请退款。

第四轮：请告诉我这个订单的金额。

请思考：
1. 如果历史对话被截断，Agent 可能丢失什么信息？
2. 如果订单号丢失，Agent 是否应该自行猜测？
3. 如果支付状态丢失，是否应该直接判断可以退款？
4. 如何通过自动化测试证明关键信息没有丢失？
这里要建立一个重要意识：

上下文管理错误可能直接演变成电商支付业务错误。

第四部分：Day 2 作业与验收标准
Day 2 必须交付
100 分

交付物	分值
TokenCounter 实现	20
TokenCounter 自动化测试	20
ContextChecker 实现	20
上下文边界测试	20
电商 Agent 场景分析	20


验收通过标准： 80 分及以上，且没有关键业务逻辑错误。

建议今天投入 6 小时：
- 1 小时：理解 Token 和 Context Window。
- 1 小时：完成 TokenCounter。
- 1 小时：完成 Pytest 自动化测试。
- 1.5 小时：实现 ContextChecker 和边界测试。
- 1 小时：完成电商 Agent 场景分析。
- 0.5 小时：整理代码和测试报告。
今天的提交方式
完成后，把以下内容发给我：
1. Day 1 的代码、测试运行结果和场景分析答案（用于补做验收）。
2. Day 2 的 token_counter.py。
3. Day 2 的 context_checker.py。
4. 对应的 Pytest 测试代码和运行结果。
5. 电商 Agent 历史对话截断场景分析。
我们的最终目标不是让你学会几个 LLM 工具，而是让你具备独立设计、开发、自动化和评估 AI Agent 测试体系的能力。 今天先把 Token 与上下文边界这块基础打扎实。
