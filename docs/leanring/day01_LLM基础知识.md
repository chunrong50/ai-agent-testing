## ---------------------Day 1: AI与LLM基础知识 ------------------
### 课程1：理解AI、机器学习、深度学习和LLM
首先建立一个基本的技术认知。
它们之间的关系可以理解为：
- AI：人工智能，是最大的概念。
- Machine Learning：机器学习，是实现 AI 的一种方法。
- Deep Learning：深度学习，是机器学习的一个分支。
- LLM：大语言模型，是基于深度学习技术训练出来的语言模型。
作为 AI Agent 测试人员，你目前不需要深入研究模型训练算法，但需要理解大模型的基本特征。

### 课程2：传统软件测试和大模型测试的区别
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

### 课程3：搭建学习项目环境
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

### 课程4：第一个大模型测试程序
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

### 课程5：Day 1 测试设计作业
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

## 第一周剩余课程预告
为了让你知道接下来每天学什么，我也把 Day 2～Day 7 的任务和验收要求准备好了
Day 2：Token、Transformer、Context Window
课程内容
- Transformer 基本工作原理。
- Tokenizer 的工作方式。
- 上下文窗口限制。
- 长文本输入和截断。
编码任务

使用 tiktoken 编写 Token 统计工具：
import tiktoken

def count_tokens(text: str, model="gpt-4o"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


text = "查询订单A10086的支付状态"

print("Token数量:", count_tokens(text))



测试任务
- 中文输入 Token 统计。
- 英文输入 Token 统计。
- 中英文混合输入。
- 超长文本输入。
- 特殊符号输入。
- 空文本输入。
交付物：《Token及上下文窗口测试报告》。
Day 3：Temperature与模型输出稳定性
课程内容
- Temperature。
- Top-P。
- 模型随机性。
- 模型输出一致性。
- 模型版本变化对结果的影响。
编码任务：

设计一个模型调用实验程序，同一个问题执行20次，记录每次的回答。

测试任务：

例如：
订单A10086的退款金额是多少？

比较不同参数配置下的输出：
- Temperature = 0
- Temperature = 0.3
- Temperature = 0.7
- Temperature = 1
分析输出是否一致，是否出现不同金额或错误事实。

交付物：《模型输出稳定性测试报告》。
Day 4：Prompt Engineering
课程内容
- System Prompt。
- User Prompt。
- Role Prompt。
- Few-shot Prompt。
- 指令优先级。
- Prompt Injection。
编码任务：

设计一个电商客服 Prompt。

例如：
你是一个电商客服助手。

你的职责：
1. 回答商品咨询。
2. 回答订单咨询。
3. 回答退款政策问题。

规则：
1. 不允许编造订单信息。
2. 没有查询订单时，不允许声称订单已经支付。
3. 不确定的问题必须明确告知用户。
4. 涉及退款操作时必须执行权限和业务规则校验。


测试任务：

设计20条不同输入，测试是否遵循指令。

交付物：《电商客服 Prompt 测试集》。
Day 5：模型幻觉测试
课程内容
- Hallucination。
- Factual Correctness。
- Groundedness。
- Unsupported Claims。
- 模型拒答。
测试任务：

设计以下场景：
输入	预期行为
查询不存在的订单	不编造订单
查询不存在的商品	不编造商品
询问未知退款政策	明确说明无法确认
提供错误订单金额	不盲目接受
要求模型猜测支付状态	不应将猜测作为事实

交付物：《LLM幻觉测试报告》。
Day 6：真实模型API及结构化输出
课程内容
- API Key。
- HTTP请求。
- 模型调用。
- JSON输出。
- Pydantic数据校验。
- Timeout及异常处理。
编码任务：

通过 OpenAI Python SDK 接入真实模型。

例如：
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

response = client.responses.create(
    model=os.getenv("OPENAI_MODEL"),
    input="请解释什么是电商订单支付状态"
)

print(response.output_text)



这里使用环境变量配置模型名称和密钥。你也可以使用兼容 OpenAI API 格式的其他模型服务，具体适配其接口要求即可。

测试任务：
- 正常调用。
- 无效 API Key。
- API 超时。
- 模型返回空结果。
- JSON 格式错误。
- 缺少必要字段。
交付物：《LLM API接口自动化测试程序》。
Day 7：第一周综合实战及复盘
完成：
1. 整理前六天的代码。
2. 整理测试数据集。
3. 执行全部自动化测试。
4. 统计通过率和失败原因。
5. 编写第一份大模型测试报告。
6. 完成知识考核。
最终形成：
第一周项目成果
LLM测试基础代码库
Python + Pytest


LLM测试数据集
正常、异常、边界、幻觉场景


LLM测试报告
模型输出、稳定性、异常分析