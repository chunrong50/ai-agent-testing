这次 Day 2 的提交我会分成两部分评审：电商场景分析和代码及测试质量。

先说结论：你的场景分析已经抓住了核心——上下文信息丢失后，Agent不能自行补全订单事实，必须基于仍然有效的用户信息和工具查询结果作答。 但你对“上下文超限后会发生什么”的描述有一个需要纠正的地方：超限不一定意味着模型自动截断，也不一定必然导致幻觉。

## 一、电商场景分析



基本通过

&#x20;建议得分：18/20



逐项点评：

1. 可能丢失的信息：正确。 订单号、支付状态、金额、退款意图都可能因历史记录被截断或未被保留而丢失。还可以补充：退款资格、用户身份与权限信息、工具查询结果及其时效性。
2. 不能猜测：正确。 但要区分“信息缺失”和“幻觉”：信息缺失是上下文或数据问题；Agent在没有证据时编造订单状态，才是幻觉表现。
3. 后续处理：基本正确。 如果订单号确实已经丢失，应先向用户确认订单号，再查询订单系统。如果订单号仍在当前上下文或结构化 Memory 中，就不必让用户重复输入。支付状态也必须以工具返回的权威数据为准。
4. 测试设计：方向正确，但还不够完整。 除了验证用户输入与工具参数一致、工具返回包含关键信息，还应验证：
   - 关键订单信息是否进入模型实际收到的上下文；
   - 工具调用结果是否被正确保留和传递；
   - 预留输出空间是否足够；
   - 信息缺失时，Agent是否主动澄清，而不是编造。

建议把第 4 点升级为一条完整的测试链路：

`用户输入 → 上下文构建 → Token计算 → Tool调用 → Tool返回 → 上下文更新 → 模型回答`

这样你验证的就不只是某个字段，而是整条信息传递链路。

## 二、为什么不能直接把请求发送给模型？

你的计算是正确的：

\\[ 7000+2000=9000>8000 \\]

但需要从三个概念进一步区分。

1\. Token：模型计算文本长度的基本单位

Token不是字符数，也不是固定的一个汉字或一个英文单词。不同语言、数字、标点和编码方式会产生不同数量的 Token。

因此，不能简单使用 Python 的 `len(text)` 来判断模型请求是否超限，应该使用目标模型对应的 Tokenizer 进行估算或计算。

2\. Context Window：模型一次请求能够处理的上下文容量

Context Window 不只是用户当前输入，它通常还需要容纳：

- System Prompt、Developer Prompt；
- 历史对话；
- 当前用户输入；
- 工具定义及工具调用相关内容；
- 工具返回结果；
- 模型生成回答所需的空间。

所以，你的例子中，7000 Tokens 的输入加上 2000 Tokens 的输出预留，已经超过 8000 Tokens 的窗口。

3\. 输出空间：必须给模型回答预留容量

如果输入占用了全部窗口，模型就没有足够空间生成回答。

实际系统可能会采取截断历史、压缩上下文、拒绝请求或限制输出等策略，具体取决于模型服务和应用层实现。不能直接断言模型一定会自动截断。

更重要的是：如果订单号、支付状态等关键事实被截断，Agent可能无法正确回答；如果它在没有证据的情况下仍然给出确定答案，就可能产生幻觉。

## 三、代码评审

需要修改后通过

我检查了你上传的 `TokenCounter`、`ContextChecker` 和对应测试代码。整体思路没问题，但 `ContextChecker` 有一个比较关键的边界逻辑错误。

### 1. TokenCounter：18/20

基本通过

做得好的地方：

- 使用 `tiktoken`，而不是 `len(text)` 统计 Token。
- 考虑了中英文、数字、特殊字符和混合文本。
- 空字符串返回 0。
- 非字符串输入抛出 `TypeError`。
- 使用 Fixture 隔离测试对象。

需要改进：

问题一：删除 print。

```
print(f"长度为：{result}")
```

TokenCounter 是基础工具类，不建议在内部直接打印。测试时通过返回值断言即可，后续可以使用日志系统。

问题二：增加返回值精确性验证。

目前长文本测试：

```
assert size > 20
```

只能说明统计结果大于 20，无法验证 Token 统计是否准确。

可以增加：

```
def test_token_count_is_consistent(counter):
    text = "订单 A10086 支付状态：SUCCESS"

    first = counter.count(text)
    second = counter.count(text)

    assert first == second
```

这个测试验证统计结果稳定，但不代表 Tokenizer 本身与目标模型的编码完全匹配，后续还需要验证目标模型对应的编码配置。

### 2. ContextChecker：10/20

存在关键缺陷

你当前的代码：

```
if reserved_tokens <= 0:
    raise ValueError("reserved_tokens must be positive")
```

这里有一个错误。

你在测试场景中明确提出：

> 输出预留空间为 0。

但代码不允许 `reserved_tokens=0`。

实际上，0 是一个合法值。比如：

- 输入 Token：20
- 预留输出 Token：0
- 最大窗口：30

那么：

\\[ 20+0\leq30 \\]

应该返回 `True`。

应该改成：

```
if reserved_tokens < 0:
    raise ValueError("reserved_tokens cannot be negative")
```

另外还有两个问题：

- `if not text` 会让空字符串直接报错，但 TokenCounter 已经支持空字符串返回 0。建议让 ContextChecker 负责容量计算，空输入校验交给上层 LLMClient。
- `max_tokens` 和 `reserved_tokens` 没有进行类型校验。例如 `30.5`、`True` 都可能通过当前逻辑，但它们不应该被当成合法 Token 数量。

建议你将 ContextChecker 修改为：

```
class ContextChecker:
    """检查输入 Token 和预留输出 Token 是否超过上下文窗口。"""

    def __init__(self, token_counter, max_tokens):
        if isinstance(max_tokens, bool) or not isinstance(max_tokens, int):
            raise TypeError("max_tokens must be an integer")

        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive")

        self.token_counter = token_counter
        self.max_tokens = max_tokens

    def can_fit(self, text: str, reserved_tokens=0) -> bool:
        if isinstance(reserved_tokens, bool) or not isinstance(reserved_tokens, int):
            raise TypeError("reserved_tokens must be an integer")

        if reserved_tokens < 0:
            raise ValueError("reserved_tokens cannot be negative")

        input_tokens = self.token_counter.count(text)

        return input_tokens + reserved_tokens <= self.max_tokens
```

注意：这里允许空字符串，非字符串类型由 TokenCounter 检查。

### 3. ContextChecker 测试：8/20

目前测试覆盖了一些边界场景，但存在三个重要问题。

问题一：测试名称和实际测试内容不一致。

```
@pytest.mark.parametrize("text", [text, text1])
def test_input_token_equals_max(context, text):
    result = context.can_fit(text, 10)
    assert not result
```

你这里的 `reserved_tokens=10`，输入 Token 即使刚好等于 30，总量也是 40，当然不应该通过。

建议拆成不同测试：

| 场景             | 输入 Token | 预留输出 | 最大窗口 | 预期    |
| -------------- | -------- | ---- | ---- | ----- |
| 刚好达到上限         | 20       | 10   | 30   | True  |
| 超出 1 Token     | 21       | 10   | 30   | False |
| 输入刚好达到上限但无输出预留 | 30       | 0    | 30   | True  |
| 输入超过上限         | 31       | 0    | 30   | False |

问题二：测试数据不应该依赖你手动猜测 Token 数量。

你现在在注释中写：

```
# token=30
# token=31
```

这依赖特定 Tokenizer 的实际编码结果。我目前无法在当前运行环境中执行你的 `tiktoken` 测试，因此不能确认这两个注释是否准确。

更好的方式是使用 FakeTokenCounter，精准控制输入 Token 数量。

例如：

```
class FakeTokenCounter:
    def __init__(self, token_count):
        self.token_count = token_count

    def count(self, text):
        return self.token_count
```

测试边界时：

```
def test_exact_context_boundary():
    checker = ContextChecker(
        FakeTokenCounter(20),
        max_tokens=30
    )

    assert checker.can_fit("订单查询", 10) is True


def test_context_exceeds_by_one():
    checker = ContextChecker(
        FakeTokenCounter(21),
        max_tokens=30
    )

    assert checker.can_fit("订单查询", 10) is False


def test_reserved_tokens_can_be_zero():
    checker = ContextChecker(
        FakeTokenCounter(30),
        max_tokens=30
    )

    assert checker.can_fit("订单查询", 0) is True
```

这样才能精准验证边界条件，而不是让测试数据受 Tokenizer 编码变化影响。

问题三：测试文件有不必要的依赖。

```
from tests.week01.test_token_counter import counter
```

这个导入没有实际使用，建议删除。

Day 2 的测试不应该依赖 Day 1 的测试模块。测试 Fixture 应该尽量独立，避免测试之间产生耦合。

## 四、Day 2 综合评分

| 评审项目                | 满分  | 得分 |
| ------------------- | --- | -- |
| TokenCounter 实现     | 20  | 18 |
| TokenCounter 测试     | 20  | 16 |
| ContextChecker 实现   | 20  | 10 |
| ContextChecker 边界测试 | 20  | 8  |
| 电商场景分析              | 20  | 18 |
| 总分                  | 100 | 70 |

70/100，暂未通过

这次不是知识理解有大问题，而是代码实现和测试用例之间存在不一致。尤其是 `reserved_tokens=0`，属于必须修复的边界逻辑缺陷。

## 五、修改后的验收要求

先不要急着进入 Day 3。请完成以下修改：

- 修改 ContextChecker，允许 `reserved_tokens=0`。
- 增加 `max_tokens`、`reserved_tokens` 的类型校验。
- 决定空字符串由哪个层负责校验，并保持职责一致。
- 使用 FakeTokenCounter 测试精确边界。
- 覆盖刚好达到上限、超过 1 Token、预留输出为 0。
- 删除不必要的测试模块导入。
- 重新运行 Pytest，提交测试结果。

额外给你一个进阶思考题：

假设电商 Agent 的模型 Context Window 是 8000 Tokens：

- System Prompt：1000 Tokens
- 历史对话：3000 Tokens
- 当前用户输入：1000 Tokens
- Tool 定义：1000 Tokens
- Tool 返回结果：1000 Tokens
- 预留模型输出：1500 Tokens

你写的 `ContextChecker` 如果只检查当前用户输入的 1000 Tokens，会不会误判请求可以发送？

这个问题很重要。因为在真实 Agent 测试中，我们需要检查的是完整请求上下文，而不只是用户输入文本。 这也是你从传统自动化测试工程师转向 AI Agent 测试工程师时，需要建立起来的一个关键思维。