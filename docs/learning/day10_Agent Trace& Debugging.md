# Day 10：Agent Trace & Debugging（执行链路追踪与问题定位）

今天进入 Day 10。先把课程方向重新对齐：

我们的目标不是培养一个只会写 Pytest 用例的人，而是让你具备初级 AI Agent 测试工程师的面试能力。

你有 10 年以上软件测试经验，已经具备业务测试、自动化测试和 Python/Pytest 基础。因此，接下来的学习不应该继续花大量时间练习普通测试设计，而应该重点补齐 AI Agent 特有的能力：

1. 理解 Agent 的运行机制，知道每个环节由谁负责。
2. 能识别 LLM 决策、Agent 流程控制、Tool 执行和业务校验的问题。
3. 能通过代码、日志和测试结果定位 Agent 的故障。
4. 能用少量高价值测试验证关键机制，并清楚解释测试依据。

Day 10 的主题是 Trace（执行链路追踪）与 Debugging（问题定位）。它是原先课程安排中的内容，不是再开发一套 Agent，也不是继续堆砌退款场景的测试用例。

## 一、为什么要学习 Trace？

先看一个电商退款场景：

用户请求：

> 帮我把订单 ORD1001 退款。

Agent 执行过程：

1. 接收用户请求

   用户要求退款。
2. LLM 决策

   选择 `query_order`，生成订单号参数。
3. Tool 执行

   查询订单，返回订单已支付。
4. Observation

   将订单查询结果返回给 LLM。
5. LLM 决策

   选择 `permission_check`。
6. Tool 执行

   权限检查返回 `allowed=False`。
7. Agent 流程控制

   终止后续执行，不调用退款工具。
8. 最终响应

   告知用户无权操作该订单。

如果最终结果不符合预期，仅看最后一条错误信息是不够的。

例如，Agent 错误地执行了退款，我们需要知道：

- 是 LLM 错误选择了 `execute_refund`？
- 是 Agent 没有正确检查权限结果？
- 是 ToolExecutor 执行了不应该执行的工具？
- 是 Step 状态没有正确更新，导致流程继续？
- 还是工具返回结果正确，但 Agent 没有正确处理 Observation？

Trace 的价值，就是还原 Agent 的完整执行过程，找到问题发生在哪个环节。

## 二、Trace 到底是什么？

可以先把 Trace 理解为：一次 Agent 运行过程的完整记录。

它不仅记录最终结果，还记录每个关键执行步骤发生了什么。

这里要区分三个概念：

| 概念    | 作用             | 示例                   |
| ----- | -------------- | -------------------- |
| Log   | 记录某个事件或信息      | 查询订单失败               |
| Trace | 串联一次完整执行链路     | 从用户请求到最终响应           |
| Span  | Trace 中的一个执行片段 | 一次 LLM 调用、一次 Tool 执行 |

例如：

```
Trace ID: trace_001

1. user_request
   input: 帮我退款 ORD1001

2. llm_decision
   selected_tool: query_order

3. tool_execution
   tool: query_order
   status: success

4. observation
   result: order_status=paid

5. llm_decision
   selected_tool: permission_check

6. tool_execution
   tool: permission_check
   status: success
   allowed: false

7. agent_decision
   action: stop
   reason: permission_denied

8. final_response
   status: completed
```

注意：这里的 `tool_execution success` 表示工具调用本身成功，不代表业务操作一定允许。例如权限工具成功返回 `allowed=False`，这恰恰是一个有效的业务拒绝结果。

## 三、Agent 出问题时，如何定位？

Day 10 最重要的知识点是：不要只看结果，要根据 Trace 判断错误属于哪个层次。

| 问题类型         | Trace 中可能看到的现象  | 应该检查什么               |
| ------------ | --------------- | -------------------- |
| LLM 决策错误     | 选择了错误工具，或参数不正确  | LLM 输出、Prompt、上下文    |
| Agent 流程控制错误 | 不满足依赖条件却继续执行    | Step 状态、依赖判断、执行循环    |
| Tool 执行错误    | 工具调用异常、超时或返回错误  | ToolExecutor、工具实现    |
| 业务校验错误       | 无权限却执行退款        | 权限检查、退款业务规则          |
| 状态管理错误       | 已完成的 Step 被重复执行 | State、Plan、Step 状态更新 |

这也正好把前几天学过的内容串起来：

- Day 5：Tool Calling —— 工具选择和参数生成。
- Day 6：Multi-step Tool Calling / Reliability —— 多工具调用与可靠性。
- Day 7：Execution Loop / Context —— Agent 多轮执行机制。
- Day 8：Planning & Decision —— Plan 拆解和执行决策。
- Day 9：Executor —— Step 执行、状态管理和失败处理。
- Day 10：Trace & Debugging —— 如何还原和定位以上环节的问题。

## 四、今天需要掌握的最小 Trace 结构

今天不引入 LangSmith、OpenTelemetry 等额外框架，也不要求重构现有 Agent。

先理解并实现一个简单的 Trace 记录结构即可：

```
trace = {    "trace_id": "trace_001",    "events": [        {            "event": "llm_decision",            "step_id": "step01",            "tool": "query_order",            "status": "success"        },        {            "event": "tool_execution",            "step_id": "step01",            "tool": "query_order",            "status": "success"        },        {            "event": "tool_execution",            "step_id": "step02",            "tool": "permission_check",            "status": "success",            "result": {                "allowed": False            }        },        {            "event": "agent_decision",            "step_id": "step02",            "action": "stop",            "reason": "permission_denied"        }    ]}
```

先关注以下字段：

| 字段         | 含义             |
| ---------- | -------------- |
| `trace_id` | 标识一次 Agent 运行  |
| `event`    | 当前发生的事件        |
| `step_id`  | 对应哪个 Plan Step |
| `tool`     | 使用了哪个工具        |
| `status`   | 执行状态           |
| `result`   | 工具返回的关键结果      |
| `reason`   | 继续、终止或失败的原因    |

实际项目中还可以记录时间、耗时、错误码、重试次数等，但今天不要求把这些字段全部实现。尤其要注意，不要把密码、令牌、支付敏感信息等直接写进 Trace。

## 五、Day 10 实践任务

今天不重新开发 Agent，也不新增复杂架构。直接在你现有的 `LLMPlanAgent` 上增加 Trace 能力。

### 任务 1：理解现有执行链路

先阅读当前 `LLMPlanAgent.run()`，找出下面几个位置：

1. LLM 返回 Plan 或工具决策的位置。
2. ToolExecutor 执行工具的位置。
3. Observation 写入的位置。
4. Step 状态更新的位置。
5. Agent 决定继续执行或终止的位置。

不需要先改代码。你要能明确指出：每个位置分别负责什么。

### 任务 2：实现最小 Trace

建议在现有 `AgentState` 中增加一个 `trace_events` 列表，或者在 `LLMPlanAgent` 中增加一个简单的 Trace 记录方法。

至少记录以下事件：

- `llm_decision`：LLM 做出了什么决策。
- `tool_execution`：调用了哪个工具，成功还是失败。
- `step_update`：Step 状态发生了什么变化。
- `agent_decision`：Agent 为什么继续、停止或跳过执行。

不需要记录所有内部变量，只记录能够帮助测试人员还原执行链路的信息。

### 任务 3：只设计 3 个高价值测试

| 测试           | 核心验证目标                                           |
| ------------ | ------------------------------------------------ |
| TC01 正常执行    | Trace 能否还原 Plan Step 的完整执行顺序                     |
| TC02 权限拒绝    | 是否记录 `allowed=False`，并能定位 Agent 因权限问题终止，退款工具没有执行 |
| TC03 Tool 异常 | 是否记录工具异常及重试过程，能否定位故障发生在哪个 Step                   |

这三个测试分别验证正常链路、业务决策和异常定位。不要为了覆盖率额外增加 Python 数据结构测试。

## 六、先做三个理解题

在写代码之前，先回答这三个问题。这部分比直接复制 Trace 代码更重要。

问题 1

用户要求退款，LLM 正确选择了 `query_order`，工具也正常返回订单信息，但是 Agent 没有调用 `permission_check`，直接执行了退款。

你认为这属于哪一层的问题？为什么？

问题 2

Trace 显示：

```
step01 query_order       completed
step02 permission_check  completed
step03 execute_refund    completed
```

但实际权限工具返回的是：

```
{"success": True, "allowed": False}
```

你会优先怀疑哪一层？Trace 还需要记录什么信息，才能帮助你进一步定位？

问题 3

一次退款请求执行失败，最终用户只看到：

```
退款失败
```

为什么这个结果不足以帮助测试人员定位问题？Trace 至少需要提供哪些信息？

## 七、Day 10 验收标准

## 本日验收目标

- 能解释 Log、Trace、Span 的区别。
- 能描述一次 Agent 执行的完整 Trace 链路。
- 能区分 LLM 决策错误、Agent 流程错误、Tool 错误和业务校验错误。
- 能在当前 `LLMPlanAgent` 中实现最小 Trace。
- 完成 3 个高价值 Pytest 测试。
- 能根据 Trace 解释一个 Agent 故障的定位过程。

提交内容：

1. 上面三个理解题的答案。
2. 修改后的 `LLMPlanAgent` 和相关 State 代码。
3. `tests/week02/test_agent_trace.py`。
4. pytest 执行结果。

我会重点检查 Trace 是否真的能还原执行过程、能否区分错误层次，以及测试有没有验证真实的 Agent 行为，而不是只检查列表里是否存在几条数据。

今天的核心不是学会记录日志，而是学会像一个 AI Agent 测试工程师一样，通过执行链路定位问题。

如果你希望明天继续时收到提醒，可以设置：

📚明天提醒我继续 Day 10 验收轻点设置