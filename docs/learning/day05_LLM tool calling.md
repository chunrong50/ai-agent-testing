接下来我们调整学习节奏：Day 5–10 进入真正的 AI Agent 测试开发阶段，不再花时间反复练习基础 Python、Pytest，也不再大量堆砌测试用例。

这一阶段的目标是：从你 Day 4 已经完成的规则驱动 Payment Agent 出发，逐步掌握 LLM Tool Calling、LangGraph、RAG，以及对应的自动化测试方法。

我会继续按照你的求职冲刺目标设计：每一天都有一个核心知识点、一个电商支付 Agent 实战任务，以及少量高价值测试。

# 一、Day 5：真正的 LLM Tool Calling



今天的核心任务

&#x20;把 Day 4 的规则驱动 Agent 改造成由 LLM 决定工具调用的 Agent。



## 1. 学习目标

完成 Day 5 后，你应该能够：

1. 理解 LLM Tool Calling 的执行机制。
2. 理解 Tool Schema 的作用和定义方式。
3. 理解 LLM 如何选择工具、生成参数。
4. 理解 Agent 如何执行工具并把结果返回给 LLM。
5. 使用 Python 实现一个最小的 LLM Tool Calling 流程。
6. 使用 Pytest 测试工具选择和参数传递是否正确。

这里有一个非常重要的概念：

LLM 不会直接执行你的 Python 工具。它只是返回一个工具调用请求，真正执行 Python 函数的是 Agent。

## 2. 核心知识点

### 知识点一：传统 Agent 和 LLM Agent 的区别

Day 4：规则驱动 Agent

用户输入：帮我退款 ORD1001

Python 关键词判断：是否包含退款？

调用 OrderTool → PermissionTool → RefundTool

Day 5：LLM Tool Calling Agent

用户输入：帮我退款 ORD1001

LLM 理解意图，选择工具并生成参数

Agent 执行 Python Tool

Tool 返回 Observation，LLM 生成最终回复

### 知识点二：Tool Schema

你需要掌握工具定义中的三个关键字段：

| 字段          | 作用                |
| ----------- | ----------------- |
| name        | 工具名称              |
| description | 告诉 LLM 这个工具什么时候使用 |
| parameters  | 定义工具需要什么参数        |

例如，退款工具可以定义为：

```
refund_tool = {    "type": "function",    "function": {        "name": "execute_refund",        "description": "对符合退款条件的订单执行退款",        "parameters": {            "type": "object",            "properties": {                "order_id": {                    "type": "string",                    "description": "订单编号"                }            },            "required": ["order_id"]        }    }}
```

重点理解：Schema 是给 LLM 的工具说明，不等于真正的业务权限控制。

权限校验必须在 Python 后端执行，不能相信 LLM 自己判断用户有没有退款权限。

### 知识点三：Tool Calling 完整执行链路

需要理解以下流程：

1. 用户发送消息。
2. Agent 把用户消息和工具定义发送给 LLM。
3. LLM 返回 tool_calls。
4. Agent 解析工具名称和参数。
5. Agent 调用对应 Python 函数。
6. Python Tool 返回结果。
7. Agent 把工具结果发送给 LLM。
8. LLM 生成最终回答。

其中第 3～6 步是 Day 5 最需要理解的部分。

## 3. 实战项目任务

继续使用你的电商支付 Agent。

本次只实现两个工具：

- `query_order`：查询订单。
- `execute_refund`：执行退款。

权限工具继续保留，由 Agent 在真正执行退款前调用。

建议新增或调整以下文件：

```
src/
├── agent/
│   ├── agent.py
│   └── llm_agent.py
├── tools/
│   ├── order_tool.py
│   ├── permission_tool.py
│   └── refund_tool.py
└── schemas/
    └── tool_schemas.py

tests/
└── week02/
    └── test_tool_calling.py
```

你不需要重写 Day 4 的所有代码。尽量复用现有 Tools。

## 4. 编码任务

任务 A：实现 Tool Schema

定义订单查询工具和退款工具的 Schema。

任务 B：实现 LLM Tool Calling

实现一个最小执行循环：

```
response = llm.chat(    messages=messages,    tools=tool_schemas)if response.tool_calls:    for tool_call in response.tool_calls:        result = execute_tool(tool_call)        messages.append({            "role": "tool",            "content": result        })final_response = llm.chat(messages=messages)
```

上面是执行机制示意，实际 SDK 的消息格式和参数需要根据你选择的模型供应商调整。

任务 C：保留业务安全控制

退款流程必须保证：

```
LLM 选择 execute_refund
        ↓
Agent 获取订单
        ↓
PermissionTool 校验权限
        ↓
退款业务规则校验
        ↓
RefundTool 执行退款
```

不能因为 LLM 选择了退款工具，就直接执行退款。

## 5. Day 5 测试任务：少而精

今天只要求写 4 个核心测试。

| Case | 测试场景           | 验证重点                    |
| ---- | -------------- | ----------------------- |
| TC01 | 用户要求查询订单       | LLM 选择 query_order，参数正确 |
| TC02 | 用户要求退款         | LLM 选择退款工具，参数正确         |
| TC03 | 用户查询退款状态       | 不应该调用 execute_refund    |
| TC04 | LLM 返回不存在的工具名称 | Agent 应拒绝执行并记录错误        |

这里推荐使用 `FakeLLM` 或 `Mock` 模拟 LLM 返回结果。

不要让自动化测试每次都依赖真实 LLM，否则模型随机性、网络和费用都会影响测试稳定性。

真实模型可以另外保留一个 Smoke Test，验证接口确实能够完成 Tool Calling。

## 6. Day 5 验收标准

完成以下任务即可：

- 理解 Tool Calling 的完整执行链路。
- 能够定义 Tool Schema。
- 实现最小 LLM Tool Calling。
- 退款前保留权限校验。
- 完成 4 个核心测试。
- 能够解释 LLM、Agent、Tool 三者之间的职责。

Day 5 面试重点：

面试官问：“LLM 是怎么调用外部工具的？”

你应该能够结合自己的 Payment Agent 项目，从 Schema、Tool Call、参数解析、Python 执行、Observation 到最终回复完整解释。

# 二、调整后的 Day 6–Day 10 学习大纲

整体安排如下：

## AI Agent 测试开发：Day 5–Day 10

1. Day 5｜LLM Tool Calling

   正在进入

   从规则驱动 Agent 转向 LLM 驱动工具选择。

   交付：最小 LLM Tool Calling Agent + 4 个测试
2. Day 6｜Tool Calling 自动化测试

   学习如何测试 LLM 工具选择、参数生成、异常处理、多工具调用。

   交付：Tool Calling 测试集 + Fake LLM 测试框架
3. Day 7｜LangGraph 基础与 Agent 改造

   理解 State、Node、Edge、Conditional Edge，使用 LangGraph 重构支付 Agent。

   交付：LangGraph Payment Agent
4. Day 8｜LangGraph 测试与执行链路验证

   测试节点路由、状态流转、异常中断、循环控制和 Trace。

   交付：Graph 测试用例 + 执行轨迹验证
5. Day 9｜RAG 基础与检索流程

   学习文档切分、Embedding、向量检索、Top-K、Context 构建。

   交付：电商退款政策 RAG 问答流程
6. Day 10｜RAG 自动化测试

   学习检索质量、召回率、相关性、错误知识引用和回答忠实度测试。

   交付：RAG 测试数据集 + 评估报告

## Day 6：Tool Calling 自动化测试

核心问题：LLM 选择工具时选错了怎么办？参数错误怎么办？工具执行失败怎么办？

学习内容：

- 工具选择准确性测试。
- 工具参数完整性、类型和边界测试。
- 多工具调用顺序验证。
- Tool 返回异常后的 Agent 行为。
- Fake LLM、Mock、Spy 的使用。

建议重点测试：

| Case | 场景                |
| ---- | ----------------- |
| TC01 | 正确选择查询工具          |
| TC02 | 错误选择退款工具          |
| TC03 | 生成缺少 order_id 的参数 |
| TC04 | Tool 执行时抛出异常      |
| TC05 | 连续调用多个工具          |

特别要理解：LLM 输出正确，不代表业务执行正确；Tool 执行成功，也不代表 Agent 最终回答正确。

## Day 7：LangGraph 基础与 Agent 改造

核心问题：当 Agent 流程越来越复杂，如何管理执行状态和流程？

学习内容：

- LangGraph 与普通 Agent 的区别。
- State：管理 Agent 状态。
- Node：执行具体业务操作。
- Edge：连接执行节点。
- Conditional Edge：根据条件决定下一步。
- START、END：控制执行入口和出口。

实战任务：

将 Day 5 的 Payment Agent 改造成 LangGraph：

```
START
  ↓
理解用户意图
  ↓
查询订单
  ↓
检查用户权限
  ↓
判断是否退款
  ↓
执行退款 / 返回查询结果
  ↓
END
```

交付：一个能够完成订单查询和退款的 LangGraph Agent。

## Day 8：LangGraph 自动化测试

核心问题：怎么证明 Agent 没有走错节点、状态没有丢失？

学习内容：

- Graph 节点测试。
- 条件路由测试。
- State 更新测试。
- 节点异常测试。
- Graph 执行轨迹验证。
- 循环和终止条件测试。

重点测试 5 个场景：

1. 正常查询流程。
2. 正常退款流程。
3. 无权限时中断。
4. Tool 执行异常。
5. 条件路由错误。

交付：一套能够验证 LangGraph 执行行为的 Pytest 测试集。

## Day 9：RAG 基础与检索流程

核心问题：Agent 如何根据企业知识库回答问题？

使用电商退款政策作为知识库。

例如：

```
退款政策：

1. 已支付订单可以申请退款。
2. 未支付订单不能退款。
3. 已经退款的订单不能重复退款。
4. 超过退款期限的订单需要人工审核。
```

学习内容：

- RAG 的基本架构。
- 文档加载和切分。
- Embedding 的作用。
- 向量数据库的基本概念。
- Top-K 检索。
- 检索结果如何注入 Prompt。
- RAG 与普通 LLM 问答的区别。

实战任务：建立一个简单的退款政策知识库，让 Agent 能够根据知识库回答退款规则问题。

交付：最小 RAG 问答流程。

## Day 10：RAG 自动化测试

核心问题：如何判断 RAG 检索到的知识是否正确，最终回答是否可信？

学习内容：

- Retrieval Recall\@K。
- 检索结果相关性。
- Context Precision 的基本概念。
- Context Faithfulness / Faithfulness。
- 错误知识干扰测试。
- 无相关知识时拒答测试。

建议构建 5 条测试数据：

| Case | 用户问题         | 测试目标       |
| ---- | ------------ | ---------- |
| TC01 | 已支付订单能退款吗？   | 检索正确退款政策   |
| TC02 | 未支付订单能退款吗？   | 不得错误回答可以退款 |
| TC03 | 已退款订单能再次退款吗？ | 检索重复退款规则   |
| TC04 | 退款期限是多少？     | 检索期限相关文档   |
| TC05 | 与退款无关的问题     | 不应编造退款政策   |

交付：一个小型 RAG 测试集，以及能够展示检索质量和回答质量的评估结果。

# 三、调整后的阶段目标

我把第一阶段求职冲刺的路线进一步收敛为三个能力层次：

| 阶段  | 学习内容                             | 面试需要达到的能力             |
| --- | -------------------------------- | --------------------- |
| 第一层 | Day 1–4 Agent 基础                 | 能解释 Agent 执行机制、状态和工具  |
| 第二层 | Day 5–8 Tool Calling + LangGraph | 能开发、测试复杂 Agent 执行流程   |
| 第三层 | Day 9–10 RAG                     | 能设计 RAG 测试集，评价检索和生成质量 |

Day 10 之后，再进入 Agent 安全、Prompt Injection、LLM Judge、综合项目和面试准备。

## 四、每一天的学习时间分配

考虑到你的目标是快速达到面试水平，我建议每天控制在 2～3 小时：

| 内容        | 时间       |
| --------- | -------- |
| 核心知识学习    | 30–40 分钟 |
| 项目编码      | 60–80 分钟 |
| 测试用例设计和执行 | 30–40 分钟 |
| 总结面试表达    | 15–20 分钟 |

不要把时间花在大量阅读框架源码上。先做到能用、能测、能解释，再深入原理。

我的建议是：Day 5 不要直接使用复杂 Agent 框架。先用 Python 实现一次最小 Tool Calling 循环，理解 LLM 与 Python Tool 之间的交互，再到 Day 7 使用 LangGraph。

这样你在面试时就不只是会说“我用过 LangGraph”，而是能解释它解决了什么问题、执行链路如何工作，以及你是怎么测试它的。

下一步就按照这份计划正式开始 Day 5。