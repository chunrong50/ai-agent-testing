# Day 08：Agent Planning、Decision 与 Conditional Execution 能力盘点

第一阶段 · Interview Ready

Day 8 / 30

今日主题：Agent 如何规划任务、做出决策，并控制执行路径

预计学习时间：2–3 小时\
主要技术：Python、LLM、Agent、Pytest\
今日重点：先理解现有代码已经实现了什么，再判断真正需要补充的能力。今天暂不要求新增代码。

## 一、为什么重新调整 Day 8？

先明确 Day 7 和 Day 8 的边界：

- Day 5： Tool Calling，理解 LLM 如何提出工具调用，以及 Agent 如何解析、校验和执行。
- Day 6： Multi-step Tool Calling 与 Reliability，理解多工具执行、异常处理和执行限制。
- Day 7： Agent Execution Loop，理解 LLM、Tool、Observation、Context 如何形成循环。
- Day 8： Planning 与 Decision，理解 Agent 如何确定任务目标、选择执行路径，以及根据执行结果调整后续动作。

因此，Day 8 不再重复学习：

- 如何调用多个工具。
- 如何把 Observation 放回 Context。
- 如何设置最大执行次数。
- 如何捕获工具异常。
- 如何使用 FakeLLM 和 Mock 验证工具调用。

这些已经属于前面几天的学习内容。

今天真正要解决的问题是：

> Agent 为什么选择执行某个动作？这个选择由 LLM 决定、Python 代码决定，还是业务规则决定？如果执行过程中条件发生变化，Agent 能否调整原来的执行路径？

## 二、结合当前 GitHub 代码进行能力盘点

我检查了当前仓库 `chunrong50/ai-agent-testing` 的 `main` 分支，包括 Agent 实现、State、ToolExecutor、现有测试和 Day 8 文档。

当前仓库已经存在两种值得对比的实现。

### 1. PaymentAgent：Python 控制的固定业务流程

文件：`src/agent/agent.py`

当前代码已经有一些 Planning 和 Decision 的实现。

| 代码位置                                  | 当前实现       | 对应能力        |
| ------------------------------------- | ---------- | ----------- |
| `_extract_order_id()`                 | 从用户输入提取订单号 | 识别任务参数      |
| `_decide_action()`                    | 判断查询还是退款   | 初步意图决策      |
| `state.add_trace("planning", ...)`    | 记录计划动作     | Planning 轨迹 |
| `if action == "query_order"`          | 决定是否进入查询分支 | 条件执行        |
| `if not permission_result["allowed"]` | 权限不通过就结束   | 业务决策        |
| `refund_tool.execute_refund()`        | 执行退款       | Execution   |

这说明：固定流程、基本条件分支和部分业务决策，已经在 PaymentAgent 中实现。

但它还不是一个完整的显式 Planning 系统：

- 没有独立的任务计划对象。
- 没有把多个 Step 保存成可追踪的计划。
- 没有每个 Step 的 pending、running、completed、failed 状态。
- 没有执行过程中修改原计划的 replanning 机制。

### 2. LLMToolAgent：LLM 动态选择下一步

文件：`src/agent/llm_agent.py`

当前实现中：

```
response = self.llm.chat(messages, tools=TOOL_SCHEMAS)if not response.get("tool_calls"):    return self._finish(state, response.get("content"))for tool_call in response.get("tool_calls"):    ...
```

它的主要机制是：

1. Agent 把用户目标和工具描述交给 LLM。
2. LLM 根据当前 Context 决定调用什么工具。
3. Agent 执行工具。
4. Observation 加入 Context。
5. 再次请求 LLM，由 LLM 决定下一步。

这种方式可以称为 Implicit Planning（隐式规划）：LLM 每轮根据当前上下文动态选择下一步，不一定生成一份独立、完整的计划。

但目前没有看到独立的 Planner，也没有显式保存任务计划和步骤状态。

### 3. State：目前保存执行状态，还没有保存计划

文件：`src/agent/state.py`

目前 `AgentState` 包含：

- `user_id`
- `user_input`
- `order_id`
- `order_data`
- `tool_calls`
- `trace`
- `final_response`
- `status`
- `error`

它能够记录执行过程，但还没有：

- `plan`
- `steps`
- `current_step`
- `step_status`

所以当前 State 更接近 Execution State，而不是完整的 Planning State。

### 4. 当前代码能力结论

| 能力         | 当前判断    | 依据                   |
| ---------- | ------- | -------------------- |
| 用户意图识别     | 已实现基础版本 | `_decide_action()`   |
| 固定流程控制     | 已实现     | `PaymentAgent.run()` |
| 基于业务条件分支   | 已实现     | 订单、权限判断              |
| LLM 动态选择工具 | 已实现     | `LLMToolAgent.run()` |
| 隐式规划       | 已具备基本机制 | LLM 多轮决策             |
| 显式任务计划     | 尚未看到    | 没有独立 Plan 数据结构       |
| Step 状态管理  | 尚未看到    | State 中没有步骤状态        |
| Replanning | 尚未看到    | 没有明确的计划更新机制          |
| 决策过程追踪     | 部分实现    | Trace 记录了规划和执行事件     |

另外，当前 `tests/week02/test_agent_decision.py` 是空文件。因此，虽然项目已有部分决策实现，但还没有专门的 Day 8 决策能力测试。

结论：今天不应该重新写一个 RefundAgent，也不应该重新实现多步骤工具调用。 这些内容与现有实现重叠。我们应该先深入理解两种 Agent 的决策机制，再判断显式 Planning 是否值得补充。

## 三、今天必须掌握的 4 个核心知识点

### 1. Implicit Planning 与 Explicit Planning

这是今天最重要的新知识。

Implicit Planning：隐式规划

LLM 不一定先生成完整计划，而是在每轮执行后，根据当前 Context 决定下一步。

例如：

```
用户：帮我查询订单，如果符合条件就退款

LLM → query_order
Tool → 订单已支付

LLM → permission_check
Tool → 用户有权限

LLM → execute_refund
Tool → 退款成功

LLM → Final Answer
```

它的特点：

- 不需要提前生成完整计划。
- LLM 根据 Observation 动态选择下一步。
- 灵活，但决策可能不稳定。
- 执行路径不一定完全可预测。

这正是目前 `LLMToolAgent` 已经具备的基本机制。

Explicit Planning：显式规划

Agent 先生成一份结构化计划，再根据计划逐步执行。

例如：

```
plan = [    {"step": 1, "action": "query_order", "status": "pending"},    {"step": 2, "action": "check_permission", "status": "pending"},    {"step": 3, "action": "execute_refund", "status": "pending"}]
```

执行过程中维护计划状态：

```
Step 1：query_order
状态：completed

Step 2：check_permission
状态：completed

Step 3：execute_refund
状态：pending
```

如果订单已经退款，则原计划中的退款步骤应该被取消，而不是继续执行。

它的特点：

- 计划可以被保存和检查。
- 可以追踪每个步骤的执行状态。
- 更容易分析计划错误。
- 可以支持计划更新和恢复。

两种规划方式的区别

Implicit Planning

用户目标 + 当前 Context

LLM 决定下一步

执行工具并获得 Observation

下一轮重新决策，不一定有完整计划对象

Explicit Planning

用户目标

生成结构化 Plan

按 Step 执行并更新状态

根据结果继续、终止或更新 Plan

计划本身是可以管理和追踪的数据

面试需要能够回答：

LLM Agent 一定需要独立的 Planner 吗？

不一定。简单任务可以通过 LLM 每轮动态选择动作完成隐式规划；对于步骤较多、依赖关系复杂或需要状态追踪的任务，可以引入显式 Planner。选择取决于任务复杂度、可控性和业务要求。

### 2. Decision Making：谁在做决策？

需要区分三个决策主体。

| 决策主体         | 主要职责          | 示例                      |
| ------------ | ------------- | ----------------------- |
| LLM          | 理解意图、提出下一步行动  | 选择 `query_order`        |
| Python Agent | 控制流程、执行分支     | `if action == "refund"` |
| 业务系统         | 判断业务规则和交易是否合法 | 订单是否已支付、是否允许退款          |

以退款为例：

```
LLM：建议执行 execute_refund
        ↓
Agent：检查当前执行流程是否允许进入退款步骤
        ↓
RefundTool：再次检查订单状态、用户权限、退款状态
        ↓
交易系统：执行真实退款
```

这里有一个重要原则：

LLM 可以提出行动建议，但不能拥有绕过业务规则的权限。

当前项目中，`RefundTool.execute_refund()` 已经做了订单归属、支付状态、退款状态和金额合法性检查。

这就是为什么不能只测试 LLM 最终选择了哪个工具，还要检查执行层是否真正阻止了非法交易。

### 3. Conditional Execution：条件分支不等于 Planning

你之前已经学过工具执行和异常处理，这里不再重复。

今天重点理解它们之间的关系：

- Planning：确定要完成哪些步骤。
- Decision：根据当前信息选择下一步。
- Conditional Execution：根据决策结果控制实际执行路径。

例如：

```
if order["payment_status"] != "PAID":    return "ORDER_NOT_PAID"if not permission["allowed"]:    return "PERMISSION_DENIED"return execute_refund(order["order_id"])
```

这段代码实现了条件分支，但它本身并不等于显式 Planning。

面试中需要避免把三个概念混为一谈。

### 4. Replanning：为什么需要重新规划？

Replanning 是今天需要初步认识的新概念。

假设 Agent 最初生成了计划：

```
1. 查询订单
2. 检查权限
3. 执行退款
```

但执行第一步后，发现订单已经退款。

此时应该：

```
原计划：
1. 查询订单       completed
2. 检查权限       pending
3. 执行退款       pending

实际情况：
订单已经退款

重新决策：
取消后续退款操作
返回订单已退款
```

这就是 Replanning 的基本思想：

当实际执行结果与原计划的前提不一致时，Agent 需要重新评估后续步骤，而不是机械执行原计划。

今天只需要理解机制，不要求实现完整的 Replanning Engine。

## 四、结合现有代码，完成 3 个代码走读任务

今天的编码重点是阅读、解释和分析现有实现，不是重新写代码。

### 任务 1：分析 PaymentAgent 的固定流程

打开：

`src/agent/agent.py`

重点阅读以下方法：

- `_extract_order_id()`
- `_decide_action()`
- `run()`
- `_finish()`

你需要回答：

1. PaymentAgent 是如何确定用户希望查询订单还是退款的？
2. 它的 Planning 是由 LLM 负责，还是 Python 代码负责？
3. 哪些 `if` 语句真正控制了执行路径？
4. 如果用户要求退款，但订单尚未支付，会在哪里被拦截？
5. 这是不是显式 Planning？为什么？

特别注意第 4 个问题：当前 Agent 本身没有在退款前显式检查 `payment_status`，而是由 `RefundTool` 在执行层再次校验。你需要区分 Agent 的流程控制与工具内部的业务安全校验。


### 任务 2：分析 LLMToolAgent 的动态决策

打开：

`src/agent/llm_agent.py`

重点阅读：

```
response = self.llm.chat(messages, tools=TOOL_SCHEMAS)
```

以及：

```
if not response.get("tool_calls"):    return self._finish(state, response.get("content"))
```

和工具执行后的 Observation 处理。

回答：

1. LLM 是如何决定调用哪个工具的？
2. Agent 是否提前生成了一份完整的任务计划？
3. 如果第一次调用 `query_order`，第二次调用 `permission_check`，这个顺序是谁决定的？
4. Observation 如何影响下一轮 LLM 的决策？
5. 如果 LLM 决定跳过权限检查直接调用退款工具，当前系统能否阻止非法退款？

第 5 题需要结合 `ToolExecutor` 和 `RefundTool` 一起分析，不能只看 LLMToolAgent。

### 任务 3：分析 AgentState

打开：

`src/agent/state.py`

回答：

1. 当前 State 保存了哪些信息？
2. `trace` 和 `tool_calls` 分别解决什么问题？
3. 当前 State 能否还原 Agent 的完整任务计划？
4. 如果要支持显式 Planning，你认为最少还需要保存哪些信息？

提示：思考 Plan、Step、Step Status、Current Step。

## 五、今天的实战练习：判断 Agent 的执行路径

下面不要求你写测试代码。先根据当前项目架构，分析这些情况。

| 场景         | 需要分析的问题                      |
| ---------- | ---------------------------- |
| 订单不存在      | 是否继续执行后续步骤？                  |
| 订单未支付      | 哪一层负责阻止退款？                   |
| 用户无权限      | 是否可能发生退款？                    |
| 订单已经退款     | 是否需要重新规划？                    |
| LLM 直接请求退款 | Agent 和 RefundTool 如何共同保证安全？ |

重点不是背答案，而是能够从代码中找到证据。

另外，当前代码里没有 `check_refund_eligibility` 这个工具，因此今天不要照搬旧 Day 8 文档中的退款资格工具流程。我们只分析仓库实际存在的工具和业务规则。

## 六、面试能力：今天必须能回答的 5 个问题

建议你尝试不看资料回答。

1. Agent 的 Planning 和 Execution 有什么区别？
2. Implicit Planning 和 Explicit Planning 有什么区别？
3. LLM 决策与业务规则决策有什么区别？
4. 为什么支付、退款等高风险业务不能完全依赖 LLM 决策？
5. 什么是 Replanning？什么情况下需要重新规划？

尤其是第 2、3、4 题，属于今天的重点。

## 七、Day 8 提交任务与验收

今天先做能力盘点，不新增代码

请提交以下内容：

第一部分：代码理解

- `PaymentAgent` 的 Planning 和 Decision 分别在哪里？
- `LLMToolAgent` 的隐式规划机制是什么？
- `AgentState` 当前保存了什么，缺少什么？

第二部分：技术理解

- 用自己的话解释 Implicit Planning 和 Explicit Planning。
- 解释 LLM 决策与业务规则决策的区别。
- 解释 Replanning。

第三部分：场景分析

选择上面 5 个场景，说明执行路径、阻断位置和理由。

### 评分标准

| 评估维度                      | 分值  |
| ------------------------- | --- |
| Planning 与 Execution 原理理解 | 25  |
| LLM 与 Python 决策机制理解       | 25  |
| 现有代码分析能力                  | 30  |
| 业务安全与执行路径分析               | 20  |
| 总分                        | 100 |

验收要求：

- 80 分以上。
- 能够结合代码说明，而不是只背概念。
- 能区分 LLM 决策和业务系统的最终校验。
- 能指出当前项目显式 Planning、Step 状态管理和 Replanning 的缺口。

通过后再决定是否新增代码。 如果你已经能理解并解释现有机制，就不需要为了完成 Day 8 而硬写一个重复的 RefundAgent。

## 八、Day 8 完成后的学习方向

今天盘点后，根据实际掌握程度决定下一步：

| 盘点结果                   | 后续安排                 |
| ---------------------- | -------------------- |
| 已有机制理解充分               | 不增加重复编码，进入下一项新能力     |
| 代码已经实现，但理解不足           | 针对性讲解和小范围修改          |
| 显式 Planning 确实缺失且有学习价值 | 再设计一个最小 Plan/Step 实现 |
| 只是当前项目没有实现，但面试阶段不要求    | 先掌握原理，留到第二阶段深入       |

今天的核心成果不是多写一个 Agent，而是能够清楚解释：一个 Agent 是怎样从用户目标出发，选择行动、控制执行，并在条件变化时调整后续任务的。

你完成后把代码分析和问题答案发给我，我会按上述标准逐项 Review，再决定是否需要增加 Day 8 编码任务。