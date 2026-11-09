# Day 7：Agent 架构与执行链路（一）——理解 Agent 的核心运行机制

第一阶段 · Interview Ready

W2 · Agent 架构

# Day 07 / 30

今日主题：Agent Architecture & Execution Lifecycle

今日核心目标：从理解 Agent 的代码实现，提升到能够解释 Agent 为什么这样运行、各个模块如何协作，以及如何验证执行过程是否正确。

预计学习时间

3–4 小时

主要技术

Python / LLM API / Pytest

今日编码重点

Agent 执行循环

## 一、Day 7 为什么学习这个内容？

Day 4、Day 5、Day 6，我们已经接触了：

- 最小 Agent 执行框架。
- Tool Calling 的基本机制。
- Agent 如何解析工具调用并执行工具。
- 如何使用 Pytest、Mock、Fake 验证工具调用。

但目前还存在一个知识缺口：

我们知道某些代码怎么写，却还没有完全建立 Agent 整体运行机制的认知。

例如，当用户提出：

> 查询订单 A10086，如果符合退款条件，就帮我申请退款。

Agent 内部究竟发生了什么？

它是如何决定先查询订单，再判断是否退款，最后调用退款工具的？

为什么 Agent 不能简单地收到用户输入后，就直接调用退款工具？

这就是 Day 7 要解决的问题。

## 二、今日核心知识点

今天重点掌握 5 个知识点，不追求面面俱到。

### 1. Agent 的整体架构

先建立一张完整的架构图。

![Agent完整架构图.jpg](Agent%E5%AE%8C%E6%95%B4%E6%9E%B6%E6%9E%84%E5%9B%BE.jpg)

一个基础 Agent 通常包含以下模块：

| 模块                   | 主要职责       |
| -------------------- | ---------- |
| User Input           | 接收用户请求     |
| Agent / Orchestrator | 管理执行流程     |
| LLM                  | 理解任务、生成决策  |
| Tool Registry        | 管理可用工具     |
| Tool Executor        | 执行工具调用     |
| State / Context      | 保存执行状态和上下文 |
| Observation          | 接收工具执行结果   |
| Final Response       | 生成最终回复     |

需要理解：

- LLM 负责理解和决策。
- Agent 负责组织和控制执行流程。
- Tool 负责执行具体业务操作。
- State 负责维护执行过程中的信息。

特别注意：LLM 本身并不等于 Agent。Agent 是围绕模型组织起来的一套执行系统。

### 2. Agent Execution Loop（执行循环）

这是今天最重要的知识点。

一个基础 Agent 的执行过程：

① User Input
用户提出业务请求

 ↓

② Agent → LLM
发送 Prompt、Context、Tools

 ↓

③ LLM Decision 
决定调用工具，或直接返回答案
 
↓

④ Tool Execution
Agent 执行工具，获取结果
 
↓

⑤ Observation → Context
将工具结果反馈给 LLM

 ↓

⑥ Final Response
返回最终结果，结束本次执行

如果 LLM 再次返回 Tool Call，则继续执行循环，而不是直接结束。

你需要特别理解三个概念：

- Decision：LLM 决定下一步做什么。
- Action：Agent 执行 LLM 请求的工具操作。
- Observation：Agent 将执行结果反馈给 LLM。

这也是很多 Agent 框架采用的基本执行模式。

### 3. Agent 为什么需要循环，而不是只调用一次 LLM？

这是一个重要的架构问题。

假设用户提出退款请求：

第一轮：

LLM 决定调用 `query_order`。

第二轮：

Agent 执行订单查询，把订单信息返回给 LLM。

第三轮：

LLM 根据订单状态决定调用 `check_refund_eligibility`。

第四轮：

Agent 执行退款资格检查，把结果反馈给 LLM。

第五轮：

LLM 根据检查结果决定是否调用 `execute_refund`。

第六轮：

Agent 根据工具执行结果生成最终回复。

这就是多轮 Tool Calling 的基本执行方式。

需要掌握的核心概念：

- 一次 Agent 执行可能包含多次 LLM 调用。
- 一次 Agent 执行可能包含多次 Tool 调用。
- 每轮执行都可能改变 State。
- Agent 必须具备退出条件，防止无限循环。

### 4. State 与 Context 的区别

这两个概念容易混淆。

| 对比   | State           | Context             |
| ---- | --------------- | ------------------- |
| 含义   | Agent 执行状态      | 提供给 LLM 的上下文信息      |
| 用途   | 管理执行过程          | 帮助 LLM 理解当前任务       |
| 内容   | 当前步骤、工具结果、执行状态等 | Prompt、历史消息、相关业务信息等 |
| 生命周期 | 通常贯穿一次执行        | 随模型请求组织和更新          |

注意：不同 Agent 框架对 State 和 Context 的定义并不完全一致。今天先掌握这个通用区分，不需要深入框架源码。

### 5. Agent 的退出机制

Agent 不能一直循环。

常见的退出条件：

1. LLM 返回 Final Answer。
2. 达到最大执行轮数。
3. 工具执行发生不可恢复错误。
4. 用户取消执行。
5. 超过执行时间限制。

这里需要理解一个工程原则：

Agent 的执行循环必须有明确的终止机制。

否则可能发生无限调用、重复执行工具、成本持续增加等问题。

## 三、今日编码实践：手写一个 Agent Execution Loop

今天不再增加复杂的业务代码，也不需要重新实现 Day 4、Day 5 的全部功能。

我们要做的是：在已有最小 Agent 的基础上，独立实现一个能够连续执行多轮 Tool Calling 的 Agent。

### 1. 今日代码目标

实现一个简化的电商订单 Agent：

用户输入：

```
查询订单 A10086
```

FakeLLM 第一次返回：

```
{    "type": "tool_call",    "tool_name": "query_order",    "arguments": {"order_id": "A10086"}}
```

Agent 执行订单查询工具。

FakeLLM 第二次收到订单查询结果，返回：

```
{    "type": "final_answer",    "content": "订单 A10086 已支付，金额为 199 元。"}
```

Agent 结束循环，返回最终结果。

### 2. 建议项目结构

沿用你目前的 GitHub 项目，不重新创建项目。

```
ai-agent-testing/
│
├── src/
│   └── agent/
│       ├── agent.py
│       ├── state.py
│       ├── llm_client.py
│       └── tool_executor.py
│
├── src/tools/
│   └── order_tool.py
│
└── tests/
    └── week01/
        └── test_agent_loop.py
```

其中：

| 文件                 | 今日任务                 |
| ------------------ | -------------------- |
| agent.py           | 实现 Agent 执行循环        |
| state.py           | 保存消息历史和执行状态          |
| llm_client.py      | 定义 LLM 接口，使用 FakeLLM |
| tool_executor.py   | 负责工具执行               |
| order_tool.py      | 提供订单查询工具             |
| test_agent_loop.py | 验证多轮执行               |

这些文件不需要全部从零重写，可以复用之前的实现。

### 3. 核心代码：Agent 执行循环

今天你需要重点理解并亲自实现下面这个逻辑：

```
class Agent:    def __init__(self, llm, tool_executor):        self.llm = llm        self.tool_executor = tool_executor    def run(self, user_input, max_steps=5):        messages = [            {"role": "user", "content": user_input}        ]        for step in range(max_steps):            # 1. 请求 LLM            response = self.llm.chat(messages)            # 2. 判断 LLM 返回类型            if response["type"] == "final_answer":                return response["content"]            # 3. 执行工具            if response["type"] == "tool_call":                result = self.tool_executor.execute(                    response["tool_name"],                    response["arguments"]                )                # 4. 保存工具执行结果                messages.append({                    "role": "tool",                    "content": str(result)                })        raise RuntimeError("Agent exceeded max_steps")
```

这是教学用的简化版本，真实 Agent 还需要处理工具调用 ID、消息关联、异常、参数校验、上下文管理等。

今天先不要扩展这些功能。

需要你理解的三个关键问题：

1. 为什么每次调用 LLM 都要传递 messages？
2. 为什么 Tool 执行结果需要重新反馈给 LLM？
3. 为什么 Agent 需要 max_steps？

如果能够独立解释并写出这段循环，今天的核心编码目标就达成了。

## 四、今日测试实践：重点验证执行机制

今天测试不是重点增加 Cases 数量，而是验证 Agent 执行循环的关键行为。

建议保留以下 4 个测试：

| 测试       | 验证的技术能力                                |
| -------- | -------------------------------------- |
| 正常多轮执行   | Tool Call → Observation → Final Answer |
| 直接返回答案   | 不需要工具时正常结束                             |
| 超过最大执行轮数 | max_steps 能阻止无限循环                      |
| 工具执行失败   | Agent 能识别和处理工具异常                       |

需要特别关注：

- FakeLLM 是否真的模拟了多轮模型响应？
- 是否能验证 LLM 被调用了几次？
- 是否能验证工具被执行了几次？
- 工具执行结果是否真正传递给下一轮 LLM？
- Agent 是否能够正确终止？

例如，多轮执行的断言不能只写：

```
assert result is not None
```

还应该验证：

```
assert llm.call_count == 2assert tool_executor.call_count == 1assert result == "订单 A10086 已支付，金额为 199 元。"
```

这里的 `call_count` 是你需要在 FakeLLM 和 Fake Tool Executor 中自行设计的记录属性。

## 五、今日问题分析：从测试工程师转向 Agent 测试工程师

下面三个问题是今天需要重点思考的。

问题 1：

如果 Agent 调用订单查询工具后，已经拿到了订单信息，但是没有把工具结果反馈给 LLM，会出现什么问题？

问题 2：

如果 LLM 连续 10 次返回 Tool Call，但是 Agent 没有最大执行轮数限制，会产生什么风险？

问题 3：

如果 Agent 的最终回复是正确的，但是中间调用了两次退款工具，能否认为 Agent 执行正确？为什么？

这三个问题分别对应：

- Context 管理。
- 执行可靠性。
- 工具调用副作用与业务安全。

它们比单纯验证最终回复是否正确更能体现 Agent 测试能力。

## 六、今日学习成果与验收标准

今天不要求你开发完整 Agent 框架，也不要求你使用 LangChain、LangGraph 等框架。

Day 7 验收清单

0 / 8 项完成

0%

能够画出 Agent 的基本架构，并解释各模块职责

能够解释 Agent Execution Loop 的完整执行过程

能够区分 Decision、Action、Observation

能够解释 State 和 Context 的基本区别

独立实现一个简化 Agent 执行循环

使用 FakeLLM 验证至少两轮 LLM 调用

使用 Pytest 验证四项关键执行行为

能够分析无限循环、工具结果丢失和重复执行问题

Review 评分标准：

| 维度          | 分值  |
| ----------- | --- |
| 技术原理理解      | 30  |
| Python 编码能力 | 30  |
| 自动化测试能力     | 25  |
| 问题分析能力      | 15  |
| 总分          | 100 |

建议达到 80 分以上，并且不能存在关键执行逻辑理解错误，才进入 Day 8。

## 七、今天的学习顺序

我建议按照以下顺序执行，不要一开始就写代码：

1. 第一步： 阅读第二部分，理解 Agent 架构和 Execution Loop。
2. 第二步： 不看代码，自己画出 Agent 执行流程图。
3. 第三步： 阅读第三部分，理解代码框架，然后自己手写。
4. 第四步： 编写 FakeLLM 和 Fake Tool Executor。
5. 第五步： 完成四个测试，并运行 pytest。
6. 第六步： 回答第五部分的三个问题。

### 今天暂时不学习的内容

为了控制学习难度，以下内容留到后续：

- LangChain / LangGraph。
- Planning 的复杂实现。
- 多 Agent 协作。
- RAG 和 Memory 的深入实现。
- Trace 平台和可视化监控。

这些内容后面会有专门的学习日，不需要提前堆积知识。

## 八、Day 7 作业提交要求

完成后，向我提交：

1. 你自己画的 Agent 执行流程（文字或图片均可）。
2. `agent.py`、`state.py`、`llm_client.py` 等核心代码。
3. `test_agent_loop.py`。
4. pytest 执行结果。
5. 上面三个问题的回答。

我会按照导师式 Review 逐项检查：

- 哪些代码真正理解了，哪些只是照着写出来。
- Agent 执行循环是否合理。
- Fake 和 Mock 是否使用正确。
- 测试能否发现真实的执行缺陷。
- 哪些知识点还需要补充。

特别强调：今天不要追求代码量，也不要依赖 AI 直接生成完整代码。 先自己写，遇到困难再查资料。实在写不出来的部分，可以提交你的思路，我会逐步引导，而不是直接给你完整答案。

今天的核心成果只有一个：

真正理解 Agent 是如何通过 LLM、Tool、Observation 和 State 完成一次完整任务的，并且能够用 Python 自己实现这个执行循环。

明天完成提交后，我们再进行 Day 7 Review，合格后进入 Day 8。