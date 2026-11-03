# Day 4：Agent 架构与运行机制

Day 1–3 已通过

Day 4 正式开始

W1 · Agent 基础

今天开始从 Prompt 测试正式进入 AI Agent 执行链路测试。

我会继续担任你的技术导师，按照之前 Day 1 的教学方式推进：先讲概念，再结合电商支付业务分析，然后设计代码任务，最后通过 Pytest 和严格代码评审验收。

先明确今天的教学原则：

不是为了让代码运行通过而写测试，而是要让测试能够发现 Agent 的真实缺陷。

## 一、承接前三天的学习进度

根据你的学习档案：

| 学习日      | 主题                             | 成绩  |
| -------- | ------------------------------ | --- |
| Day 1    | LLM 基础与 API 测试                 | 88  |
| Day 2    | Token、Tokenizer、Context        | 89  |
| Day 3    | Prompt Engineering 与 Prompt 测试 | 80  |
| Day 3 补充 | 越权退款测试                         | 86  |
| Day 4    | Agent 架构与运行机制                  | 待验收 |

目前已经掌握：

- LLM Client、FakeModel、SpyModel。
- TokenCounter、ContextChecker。
- Prompt 静态规则测试。
- 参数化测试及业务风险分析。
- 退款权限、重复退款等安全规则。

今天不重复前三天的内容，而是把这些知识连接起来。

day01-03 档案.md

## 二、Day 4 学习目标

# 今天需要掌握的 6 项能力

1. 理解普通 LLM 调用与 Agent 的区别。
2. 理解 Planning、Tool Calling、Observation、Reflection。
3. 理解 Agent 执行链路和状态流转。
4. 设计 Agent Trace 数据结构。
5. 使用 Fake Tool、Spy Tool 模拟和监控工具调用。
6. 使用 Pytest 验证执行行为，并定位第一个异常节点。

今天的核心交付物：

实现一个不依赖 LangChain、LangGraph 的轻量级电商支付 Agent，理解 Agent 的基本运行机制，为后续引入 LangGraph 做准备。

## 三、知识点 1：普通 LLM 调用与 Agent 的区别

这是 Day 4 最重要的基础概念。

### 1.1 普通 LLM 调用

例如，用户问：

> 帮我查询订单 ORD1001 的支付状态。

传统 LLM Client 的执行过程：

User Input

帮我查询订单 ORD1001 的支付状态

LLM Client

LLM Response

模型生成文本回答

核心特点：

- 输入 Prompt。
- 调用模型。
- 获得模型输出。
- 不一定有工具调用。
- 不一定有状态管理。
- 不一定有多步骤执行。

### 1.2 Agent 执行

同样的问题，如果交给 Agent：

1\. User Input

查询订单 ORD1001

2\. Planning

判断需要查询订单

3\. Tool Calling

调用 query_order(order_id='ORD1001')

4\. Observation

获得订单状态：PAID

5\. Final Response

订单已支付

Agent 不仅生成回答，还可能自主决定下一步操作，并根据工具返回结果继续执行。

### 1.3 两者的核心区别

| 对比项  | 普通 LLM | Agent          |
| ---- | ------ | -------------- |
| 输入   | Prompt | 用户任务及上下文       |
| 输出   | 模型响应   | 最终结果或中间动作      |
| 工具调用 | 通常没有   | 可以有            |
| 执行步骤 | 通常一次   | 可以多次           |
| 状态管理 | 简单     | 通常需要           |
| 执行轨迹 | 请求/响应  | 多步骤执行轨迹        |
| 测试重点 | 输入输出   | 输入、决策、工具、状态、结果 |

导师强调：

Agent 并不是一个新的大模型，而是围绕模型构建的一套执行机制。

从测试角度看：

以前你测试的是：

```
response = llm_client.chat(prompt)assert response != ""
```

现在你还要测试：

```
result = agent.run(user_input)assert "query_order" in result.tool_callsassert result.order_status == "PAID"assert result.success is True
```

当然，第二段只是示意。后面我们会设计真正可验证的 Trace 和断言。

## 四、知识点 2：Agent 的四个核心执行环节

今天重点理解四个术语。

### 2.1 Planning：规划

Agent 根据用户需求决定下一步要做什么。

电商支付案例：

用户：

> 帮我查一下订单 ORD1001 有没有支付成功。

Agent 需要判断：

```
用户意图：查询订单支付状态

需要执行：
1. 查询订单
2. 读取支付状态
3. 返回查询结果
```

测试关注点：

- 是否识别正确意图？
- 是否选择正确工具？
- 是否提取正确订单号？
- 是否制定了不必要的操作？

### 2.2 Tool Calling：工具调用

Agent 选择工具并传递参数。

例如：

```
query_order(order_id="ORD1001")
```

测试不能只判断工具有没有被调用，还需要验证：

```
assert tool_call.name == "query_order"assert tool_call.arguments == {    "order_id": "ORD1001"}
```

如果订单号被错误解析成 `ORD1002`，即使工具正常返回，Agent 仍然存在严重缺陷。

### 2.3 Observation：观察

工具返回执行结果，Agent 根据结果继续决策。

例如：

```
{    "order_id": "ORD1001",    "payment_status": "PAID",    "amount": 199.00}
```

测试关注点：

- Agent 是否正确接收工具返回？
- 是否使用了真实工具结果？
- 是否忽略了工具错误？
- 是否出现结果与回答不一致？

特别注意：

如果工具返回：

```
{"payment_status": "UNPAID"}
```

Agent 却回答：

```
订单已经支付成功。
```

这是典型的 Observation 处理缺陷。

### 2.4 Reflection：反思与调整

Agent 根据执行结果判断是否需要调整下一步行为。

例如：

```
第一次查询订单
      ↓
工具返回：订单不存在
      ↓
判断：当前任务无法继续
      ↓
停止执行
      ↓
告知用户订单不存在
```

注意：Reflection 并不是每个 Agent 都必须实现一个独立的反思模块。它也可能体现在模型下一轮决策中。

测试重点：

- 工具失败后是否正确处理？
- 是否无限重试？
- 是否重复调用相同工具？
- 是否在失败后仍然声称成功？
- 是否正确终止执行？

### 2.5 四个环节的测试映射

| 环节           | 测试对象 | 关键断言       |
| ------------ | ---- | ---------- |
| Planning     | 决策   | 是否选择正确工具   |
| Tool Calling | 工具调用 | 名称、参数、调用次数 |
| Observation  | 工具结果 | 是否正确处理返回   |
| Reflection   | 后续决策 | 是否继续、重试或终止 |

这张表建议保留，后续学习 Tool Calling、Workflow、Multi-Agent 时会反复使用。

## 五、知识点 3：Agent Trace 设计

今天的重点技术知识

这是传统自动化测试工程师转向 Agent 测试时需要重点建立的能力。

### 5.1 为什么需要 Trace？

假设 Agent 最终回答：

```
订单 ORD1001 已支付成功。
```

但实际情况是：

```
订单 ORD1001 尚未支付。
```

如果只看最终回答，我们知道结果错误，却不知道问题在哪里。

可能的原因：

1. Planning 选择了错误的工具。
2. Tool Calling 传递了错误订单号。
3. 工具返回的数据错误。
4. Observation 没有正确处理工具结果。
5. Final Response 没有依据工具结果生成。

我们需要一条完整的执行轨迹。

### 5.2 设计 Trace 数据结构

今天先采用简单的 JSON 结构：

```
{    "trace_id": "TRACE001",    "user_input": "查询订单 ORD1001",    "steps": [        {            "step": 1,            "type": "planning",            "action": "query_order"        },        {            "step": 2,            "type": "tool_call",            "tool_name": "query_order",            "arguments": {                "order_id": "ORD1001"            }        },        {            "step": 3,            "type": "observation",            "result": {                "payment_status": "PAID"            }        },        {            "step": 4,            "type": "final_response",            "content": "订单已支付"        }    ],    "status": "success"}
```

### 5.3 Trace 在测试中的作用

例如：

```
trace = agent.run("查询订单 ORD1001")assert trace.steps[0]["type"] == "planning"assert trace.steps[1]["tool_name"] == "query_order"assert trace.steps[1]["arguments"]["order_id"] == "ORD1001"assert trace.steps[2]["result"]["payment_status"] == "PAID"
```

这样就可以验证 Agent 的执行过程，而不只是验证最后的自然语言回答。

导师要求：

今天设计的 Trace 必须支持：

- 记录每一步的执行顺序。
- 记录工具名称。
- 记录工具参数。
- 记录工具返回结果。
- 记录执行状态。
- 记录异常信息。

后续还会逐步增加耗时、Token、模型信息和父子 Span。

## 六、知识点 4：Fake Tool、Spy Tool 与 Mock

这部分直接关联你之前学过的 FakeModel、SpyModel。

先区分三个概念：

| 类型        | 主要用途      | 今天的应用     |
| --------- | --------- | --------- |
| Fake Tool | 提供可控的模拟行为 | 模拟查询订单、退款 |
| Spy Tool  | 记录调用行为    | 验证调用次数和参数 |
| Mock Tool | 控制依赖行为及预期 | 模拟工具异常    |

例如，我们定义一个 SpyTool：

```
class SpyTool:    def __init__(self, tool):        self.tool = tool        self.calls = []    def __call__(self, **kwargs):        self.calls.append(kwargs)        return self.tool(**kwargs)
```

调用：

```
spy = SpyTool(query_order)result = spy(order_id="ORD1001")
```

检查：

```
assert len(spy.calls) == 1assert spy.calls[0] == {    "order_id": "ORD1001"}
```

这和你 Day 1 的 SpyModel 思路一致，只不过今天的被观察对象从 LLM Client 扩展到了 Agent Tool。

## 七、Day 4 实战：电商支付 Agent

核心编码任务

今天不直接上 LangGraph，也不接真实 LLM API。

我们先自己实现一个最小 Agent 执行框架，确保你理解底层机制。

### 7.1 业务背景

假设电商平台有以下订单：

| 订单号     | 用户ID | 金额  | 支付状态   | 退款状态         |
| ------- | ---- | --- | ------ | ------------ |
| ORD1001 | U001 | 199 | PAID   | NOT_REFUNDED |
| ORD1002 | U002 | 299 | UNPAID | NOT_REFUNDED |
| ORD1003 | U001 | 399 | PAID   | REFUNDED     |
| ORD1004 | U003 | 599 | PAID   | NOT_REFUNDED |

Agent 支持：

1. 查询订单。
2. 查询支付状态。
3. 查询退款资格。
4. 验证用户权限。
5. 执行退款（后半阶段实现）。

今天分两个阶段完成。

- 第一阶段：实现订单查询 Agent。
- 第二阶段：扩展退款流程和安全测试。

### 7.2 项目目录

在你现有项目中新增以下文件：

```
ai-agent-testing/
│
├── src/
│   ├── llm/
│   ├── utils/
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   └── state.py
│   │
│   └── tools/
│       ├── __init__.py
│       ├── order_tool.py
│       ├── permission_tool.py
│       └── refund_tool.py
│
├── tests/
│   └── week01/
│       ├── test_prompt_rules.py
│       └── test_agent_execution.py
│
└── docs/
    └── day04_agent_architecture.md
```

不需要修改 Day 1～Day 3 的已有代码。

### 7.3 第一阶段：实现 AgentState

文件：

`src/agent/state.py`

任务：

设计 Agent 的状态对象。

至少需要支持：

| 字段             | 类型建议        | 含义     |
| -------------- | ----------- | ------ |
| user_id        | str         | 当前用户   |
| user_input     | str         | 用户输入   |
| order_id       | str 或 None  | 订单号    |
| order_data     | dict 或 None | 订单数据   |
| tool_calls     | list        | 工具调用记录 |
| final_response | str 或 None  | 最终回答   |
| status         | str         | 执行状态   |
| error          | str 或 None  | 异常信息   |

要求：

1. 使用 Python `dataclass`。
2. 字段必须有明确类型。
3. 合理设置默认值。
4. 不同 Agent 运行之间不能共享可变状态。
5. 状态对象要便于后续扩展。

思考题：

为什么不能直接使用一个全局 dict 保存所有 Agent 状态？

### 7.4 第二阶段：实现订单查询工具

文件：

`src/tools/order_tool.py`

实现：

```
def query_order(order_id: str) -> dict:    ...
```

要求：

- ORD1001 返回对应订单数据。
- ORD1002 返回对应订单数据。
- ORD1003 返回对应订单数据。
- ORD1004 返回对应订单数据。
- 不存在的订单返回明确错误结果。
- 不允许返回不存在订单的虚构数据。

订单数据先写在 Python 内存中，不需要连接数据库。

### 7.5 第三阶段：实现 Agent

文件：

`src/agent/agent.py`

定义：

```
class PaymentAgent:    def __init__(self, tools):        ...    def run(self, user_id: str, user_input: str):        ...
```

第一阶段只实现订单查询。

基本执行过程：

```
用户输入
   ↓
识别查询订单意图
   ↓
提取订单号
   ↓
Planning
   ↓
选择 query_order
   ↓
Tool Calling
   ↓
执行订单查询
   ↓
Observation
   ↓
根据工具结果生成回答
   ↓
返回 AgentState 和 Trace
```

注意：

今天为了可控性，Planning 暂时使用确定性的规则模拟，不需要真实 LLM。

例如：

```
user_input = "帮我查询订单 ORD1001 的支付状态"
```

提取订单号：

```
ORD1001
```

选择工具：

```
query_order
```

这是一种教学用的 Agent 执行器，不代表已经实现了真正的模型自主规划。后续接入 LLM 后，我们再测试模型是否能正确选择工具。

### 7.6 第四阶段：实现 Trace

在 Agent 执行过程中记录每一步。

至少支持：

```
{    "step": 1,    "type": "planning",    "action": "query_order"}
```

```
{    "step": 2,    "type": "tool_call",    "tool_name": "query_order",    "arguments": {        "order_id": "ORD1001"    }}
```

```
{    "step": 3,    "type": "observation",    "result": {        "order_id": "ORD1001",        "payment_status": "PAID"    }}
```

Trace 应当反映实际发生的事情，不能为了让测试通过而预先伪造执行记录。

## 八、Day 4 Pytest 测试任务

今天最重要的验收部分

不要急着写代码，先理解下面的测试场景。

### 8.1 第一组：Agent 基础功能测试

| ID   | 测试场景       | 预期结果        |
| ---- | ---------- | ----------- |
| TC01 | 查询 ORD1001 | 返回 PAID     |
| TC02 | 查询 ORD1002 | 返回 UNPAID   |
| TC03 | 查询 ORD1003 | 返回 REFUNDED |
| TC04 | 查询不存在订单    | 返回明确错误      |
| TC05 | 用户输入不包含订单号 | 不调用订单查询工具   |

### 8.2 第二组：Tool Calling 测试

这是今天的重点。

| ID   | 测试场景       | 预期结果                 |
| ---- | ---------- | -------------------- |
| TC06 | 查询 ORD1001 | 调用 query_order 一次    |
| TC07 | 查询 ORD1001 | 参数必须是 ORD1001        |
| TC08 | 查询 ORD1001 | 不允许调用 execute_refund |
| TC09 | 查询 ORD1001 | 工具调用顺序正确             |
| TC10 | 查询不存在订单    | 不能生成虚构订单数据           |

特别注意 TC08：

用户只是查询订单，Agent 不应该执行退款。

```
assert "execute_refund" not in tool_names
```

这与你 Day 3 的越权退款测试思维是一致的：不仅验证应该发生什么，还要验证不应该发生什么。

### 8.3 第三组：Observation 测试

| ID   | 测试场景          | 预期结果           |
| ---- | ------------- | -------------- |
| TC11 | 工具返回 PAID     | Agent 回答已支付    |
| TC12 | 工具返回 UNPAID   | Agent 回答未支付    |
| TC13 | 工具返回 REFUNDED | Agent 回答已退款    |
| TC14 | 工具返回异常        | Agent 不能声称查询成功 |

这里需要特别关注：

Agent 的最终回答必须依据工具实际返回的数据，而不是依据用户输入或者预设的回答。

### 8.4 第四组：Trace 测试

| ID   | 测试场景 | 预期结果                 |
| ---- | ---- | -------------------- |
| TC15 | 正常查询 | Trace 包含 planning    |
| TC16 | 正常查询 | Trace 包含 tool_call   |
| TC17 | 正常查询 | Trace 包含 observation |
| TC18 | 正常查询 | Step 顺序正确            |
| TC19 | 工具异常 | Trace 记录异常节点         |
| TC20 | 执行完成 | Trace 状态与实际结果一致      |

### 8.5 第五组：Agent 状态隔离

| ID   | 测试场景          | 预期结果         |
| ---- | ------------- | ------------ |
| TC21 | 连续运行两个不同用户    | 用户状态不能串扰     |
| TC22 | 第二次查询不同订单     | 不能沿用第一次订单号   |
| TC23 | 第一次运行失败，第二次成功 | 第二次不能继承第一次错误 |
| TC24 | 连续运行多次        | Trace 独立     |

这组测试非常重要。

在传统接口测试中，我们容易关注单次请求；但 Agent 往往有多轮交互和状态管理问题。

## 九、严格代码评审：导师会重点检查什么？

我不会只看 24 个测试是否通过。

今天评分采用 100 分制：

| 评审维度             | 分值  |
| ---------------- | --- |
| Agent 架构与职责划分    | 15  |
| AgentState 设计    | 10  |
| Tool Calling 实现  | 15  |
| Trace 设计         | 15  |
| Pytest 场景覆盖      | 20  |
| Mock、Fake、Spy 使用 | 10  |
| 异常及边界处理          | 10  |
| 代码规范与可扩展性        | 5   |
| 总分               | 100 |

### 以下问题会被重点扣分

1. 直接在 Agent 内部硬编码订单查询逻辑，导致无法独立替换工具。
2. Agent 没有记录真实工具调用过程。
3. 只验证最终回答，不验证 Tool Calling。
4. 测试没有检查工具参数。
5. 测试没有检查不应该调用的工具。
6. 工具发生异常，Agent 仍然回答成功。
7. 不同用户运行时共享状态。
8. 测试依赖真实 LLM，导致结果不稳定。
9. 测试全部通过，但无法发现人为注入的缺陷。

验收规则：

- 90 分及以上：优秀，通过。
- 80～89 分：通过，但需要记录改进项。
- 70～79 分：限期修改后复评。
- 70 分以下：未通过，重新完成核心任务。

另外，涉及退款安全的关键测试如果存在缺陷，即使总分达到 80 分，也不能直接进入下一天。

## 十、Day 4 学习安排（建议 6～8 小时）

考虑到今天的内容有一定架构设计难度，我建议按以下节奏执行。

| 阶段 | 学习内容                      | 建议时间   |
| -- | ------------------------- | ------ |
| 1  | LLM 与 Agent 区别            | 40 分钟  |
| 2  | Planning、Tool Calling 等概念 | 60 分钟  |
| 3  | AgentState、Trace 设计       | 60 分钟  |
| 4  | Fake Tool、Spy Tool 实现     | 60 分钟  |
| 5  | PaymentAgent 编码           | 120 分钟 |
| 6  | Pytest 测试设计与执行            | 90 分钟  |
| 7  | 总结和提交                     | 30 分钟  |

### 最终需要提交的作业

Day 4 提交清单

0/9

src/agent/state.py

src/agent/agent.py

src/tools/order_tool.py

src/tools/permission_tool.py（如已实现）

src/tools/refund_tool.py（如已实现）

tests/week01/test_agent_execution.py

docs/day04_agent_architecture.md

完整 pytest 执行结果

Day 4 思考题答案

### 十一、Day 4 思考题

请在编码前后分别回答这些问题：

Q1. 为什么 Agent 测试不能只验证最终回答？

Q2. 如果工具调用成功，但是 Observation 阶段读取了错误的返回数据，应该如何定位？

Q3. Fake Tool 和 Spy Tool 有什么区别？什么时候应该使用它们？

Q4. 为什么每次 Agent.run() 都应该有独立的状态和 Trace？

Q5. 如果用户要求查询订单，但 Agent 调用了退款工具，你会设计哪些断言来发现这个问题？

## 十二、关于你的 GitHub 学习资料

你提供了三个项目入口：

- [docs 学习文档](https://github.com/chunrong50/ai-agent-testing/tree/main/docs?utm_source=chatgpt.com)
- [src 项目源码](https://github.com/chunrong50/ai-agent-testing/tree/main/src?utm_source=chatgpt.com)
- [tests/week01 测试代码](https://github.com/chunrong50/ai-agent-testing/tree/main/tests/week01?utm_source=chatgpt.com)

本次会话中 GitHub 目录页面没有成功加载，因此我没有把仓库中尚未读取的代码或 Day 1 文档内容当作已核实的事实。

本次 Day 4 的课程设计依据你上传的 Day 1～Day 3 学习档案，沿用其中明确规定的目标、代码结构和验收方式。

day01-03 档案.md



如果你希望我严格对照仓库里的 Day 1 模板逐项复刻教学格式，可以把 `docs` 和相关源码打包上传，我会进一步对齐。

## 导师的第一项要求

今天先不要急着实现退款功能。

优先完成 AgentState、query_order 和 PaymentAgent 的订单查询闭环。

我们先确保你真正理解 Agent 是如何执行任务的，再扩展退款、权限校验和安全测试。

你完成第一阶段后，把代码和 pytest 结果发给我。我会按照高级测试开发工程师的标准进行逐文件、逐测试用例评审，不会因为测试通过就轻易给出高分。

Day 4 正式开始。今天的目标不是写出一个能聊天的 Agent，而是写出一个能够被测试、被追踪、被验证的 Agent。