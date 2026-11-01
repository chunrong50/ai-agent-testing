第一天的内容：
https://chatgpt.com/share/6ae4aefc-9c64-83ec-b03a-9377c65ddf70


每一天都采用五步教学法：
1. 课程（Learn）
   
   学习当天的技术知识、核心概念、架构原理。
2. 编码（Code）
   
   跟着实战任务写 Python 代码，运行 Agent 或测试工具。
3. 测试（Test）
   
   自己设计测试用例，执行测试，观察异常和缺陷。
4. 分析（Analyze）
   
   分析失败原因，理解模型行为、工具调用及业务逻辑。
5. 复盘（Review）
   
   整理技术笔记、测试报告、代码及当天学习成果。
   
   
   Day 1：AI与LLM基础知识
今天正式开课
课程1：理解AI、机器学习、深度学习和LLM
首先建立一个基本的技术认知。

它们之间的关系可以理解为：
- AI：人工智能，是最大的概念。
- Machine Learning：机器学习，是实现 AI 的一种方法。
- Deep Learning：深度学习，是机器学习的一个分支。
- LLM：大语言模型，是基于深度学习技术训练出来的语言模型。
作为 AI Agent 测试人员，你目前不需要深入研究模型训练算法，但需要理解大模型的基本特征。
需要掌握的五个核心概念
1. 什么是 LLM？

LLM（Large Language Model）是通过大量数据训练得到的语言模型，能够理解和生成自然语言。

例如：

用户输入：
查询一下订单 A10086 是否支付成功。

模型可以理解用户意图，并生成回答，或者在 Agent 架构中选择调用订单查询工具。

2. 为什么 LLM 会产生幻觉？

大模型生成内容的本质是基于模型计算，预测后续 Token，而不是直接查询一个绝对可靠的事实数据库。

因此可能出现：
- 编造订单信息。
- 编造商品价格。
- 错误解释退款规则。
- 给出不存在的 API。
- 将不确定的信息说得非常肯定。
这就是 Hallucination（幻觉）。

测试人员需要验证的是：当模型缺乏可靠依据时，是否会明确表达不确定性，而不是编造答案。

3. 什么是 Token？

Token 是模型处理文本时使用的基本单位。

Token 不完全等于汉字、英文单词或者字符。

Token 数量会影响：
- 输入成本。
- 输出成本。
- 上下文长度。
- 模型处理时间。
4. 什么是 Context Window？

上下文窗口是模型一次请求能够处理的上下文容量。

例如，用户和 Agent 进行了很长时间的对话，可能出现：
- 前面提到的订单号丢失。
- 退款条件遗忘。
- 用户身份信息混淆。
- 前后回答不一致。
这些都是测试需要覆盖的场景。

5. 什么是 Temperature？

Temperature 影响模型输出的随机性。

一般来说，较低的 Temperature 倾向于更稳定的输出；较高的 Temperature 可能带来更多样化的输出。

但它不等于正确率，也不保证低 Temperature 下的结果绝对一致。

课程2：传统软件测试和大模型测试的区别
这是你必须建立的一个思维转变。
对比维度	传统软件	大模型
输入	确定性参数	自然语言、上下文
输出	固定数据结构	可能存在多种表达
执行结果	通常确定	可能具有随机性
断言方式	精确值比较	规则、语义、模型评估
测试数据	固定测试数据	需要覆盖多样表达
缺陷类型	功能、逻辑、接口错误	幻觉、偏差、指令不遵循
回归测试	结果是否变化	质量是否退化

举个电商支付的例子：

用户问：
我的订单支付成功了吗？

传统接口测试：
assert response["payment_status"] == "SUCCESS"

大模型测试不能简单写成：
assert response == "你的订单已经支付成功"

因为模型可能回答：
- 订单已经支付成功。
- 您的付款已完成。
- 查询结果显示支付状态为成功。
这些表达可能都是正确的。

但是，如果模型根本没有查询订单，只是根据用户的问题猜测支付成功，就应该判定为失败。

这就是 AI 测试需要学习的新思维。

课程3：搭建学习项目环境
我们从第一天开始建立统一的 Git 项目，后面16周持续在这个项目上迭代。

建议环境：
软件	用途
Python 3.11+	编程语言
PyCharm / VS Code	开发工具
Pytest	自动化测试
Git	代码版本管理
Jupyter Notebook	实验和分析
OpenAI兼容API	模型调用

Step 1：创建项目
打开终端：
mkdir ai-agent-testing
cd ai-agent-testing

python -m venv .venv

激活虚拟环境：

macOS / Linux：
source .venv/bin/activate

Windows：
.venv\Scripts\activate

Step 2：安装依赖
pip install pytest
pip install openai
pip install python-dotenv
pip install pydantic
pip install tiktoken
pip install pytest-html

Step 3：建立目录
ai-agent-testing/
│
├── config/
├── datasets/
├── src/
│   ├── llm/
│   └── utils/
│
├── tests/
│   └── week01/
│
├── reports/
├── docs/
├── .env
├── .gitignore
└── requirements.txt

.gitignore 中加入：
.venv/
.env
__pycache__/
.pytest_cache/
reports/

.env 用于保存模型 API Key，千万不要把真实密钥提交到 Git。
Step 4：检查环境
python --version
pytest --version
pip show openai

Day 1 环境验收标准：
- Python 可以正常运行。
- Pytest 可以正常执行。
- 项目目录创建成功。
- 虚拟环境正常。
- API Key 不会被提交到 Git。
课程4：第一个大模型测试程序
今天我们先不急着调用真实模型，而是先学习如何建立一个可测试的模型调用接口。

创建：

src/llm/llm_client.py
class LLMClient:

    def __init__(self, model_adapter):
        self.model_adapter = model_adapter

    def ask(self, question: str) -> str:

        if not question.strip():
            raise ValueError("问题不能为空")

        result = self.model_adapter.generate(question)

        if not isinstance(result, str):
            raise TypeError("模型返回结果必须是字符串")

        if not result.strip():
            raise ValueError("模型返回内容不能为空")

        return result

这里的 model_adapter 是一个模型适配器。以后可以接入不同模型，而不用修改测试用例。

创建：

tests/week01/test_llm_client.py
import pytest

from src.llm.llm_client import LLMClient


class FakeModel:

    def generate(self, question):
        return "订单支付成功"


def test_normal_question():

    client = LLMClient(FakeModel())

    result = client.ask("订单A10086支付成功了吗？")

    assert result == "订单支付成功"


def test_empty_question():

    client = LLMClient(FakeModel())

    with pytest.raises(ValueError):
        client.ask("")


def test_whitespace_question():

    client = LLMClient(FakeModel())

    with pytest.raises(ValueError):
        client.ask("   ")


def test_empty_model_response():

    class EmptyModel:
        def generate(self, question):
            return ""

    client = LLMClient(EmptyModel())

    with pytest.raises(ValueError):
        client.ask("查询订单")

执行：
pytest -v tests/week01/

这里有一个重要知识点：

我们目前测试的是模型调用客户端的输入输出约束，还没有真正测试模型的智能行为。

后面会逐步增加真实模型调用、Prompt评估和 Agent 行为评估。

课程5：Day 1 测试设计作业
结合电商支付业务，设计以下测试用例。
编号	测试场景	预期结果
TC001	输入正常订单查询问题	正常处理
TC002	输入空字符串	拒绝输入
TC003	输入空格	拒绝输入
TC004	输入超长文本	按输入长度策略处理
TC005	模型返回空结果	正确处理异常
TC006	模型返回非字符串	正确处理类型异常
TC007	模型接口超时	返回可识别错误
TC008	模型接口返回500	正确处理服务异常

思考题：

假设用户问：
我的订单 A10086 已经支付成功了吧？

模型直接回答：
是的，您的订单已经支付成功。

但是实际上系统没有查询任何订单数据。

请问：
1. 这个回答在文本层面是否合理？
2. 在业务测试层面是否通过？
3. 你应该增加什么测试机制？
这个问题很重要，后面我们会通过 Agent Trace 和 Tool Calling 测试来解决。

Day 1 学习验收
Day 1 学习任务清单
0/8 已完成
[ ] 理解AI、机器学习、深度学习和LLM的关系
[ ] 掌握Token、Context Window、Temperature的概念
[ ] 理解大模型幻觉的原因
[ ] 创建Python项目及虚拟环境
[ ] 成功安装Pytest及相关依赖
[ ] 完成LLMClient代码
[ ] 完成至少8条测试用例
[ ] 回答订单支付成功案例的三个思考题