# Day 8：Agent Planning 与 Decision（一）——理解 Agent 如何规划任务与进行决策



第一阶段 · Interview Ready

W2 · Agent 架构



# Day 08 / 30

今日主题：Agent Planning & Decision Making

今日核心目标：从理解 Agent 如何执行工具调用，进一步提升到理解 Agent 如何根据用户目标、工具返回结果和业务规则，决定下一步应该执行什么。

预计学习时间：3–4 小时

主要技术：Python / LLM / Pytest

今日编码重点：多步骤任务规划与条件分支执行

## 一、Day 8 为什么学习这个内容？

Day 7 我们已经完成了 Agent Execution Loop 的学习。

目前你已经掌握：

- Agent 如何组织 LLM 和 Tool。
- Tool Call → Observation → Final Answer。
- 多轮 LLM 调用和 Context 传递。
- Agent 执行轮数与工具调用次数控制。
- FakeLLM、Fake Tool Executor 和 Pytest 验证。

但是，现在还有一个更重要的问题：

Agent 如何知道下一步应该做什么？

我们还是使用电商支付 Agent 举例。

用户提出：

> 查询订单 ORD1001，如果已经支付并且符合退款条件，就帮我申请退款。

这不是一个简单的工具调用任务。

Agent 需要完成：

1. 查询订单。
2. 判断订单是否已经支付。
3. 检查订单是否符合退款条件。
4. 检查用户是否具有退款权限。
5. 根据检查结果决定是否执行退款。
6. 返回最终结果。

这里面涉及两个重要能力：

- Planning：如何把一个复杂任务拆解成多个步骤。
- Decision Making：如何根据当前信息决定下一步执行什么。

Day 7 解决的是：

Agent 如何执行任务？

Day 8 解决的是：

Agent 如何规划任务，以及如何决定下一步行动？

这两个能力共同构成了 Agent 的核心运行机制。

## 二、今日核心知识点

今天重点掌握 5 个知识点，不追求面面俱到。

### 1. Planning：Agent 如何进行任务规划？

Planning 可以理解为：

将用户提出的复杂目标拆解为一系列可以执行的步骤。

例如：

用户请求：

```
查询订单 ORD1001，
如果已经支付并且符合退款条件，就帮我退款。
```

Agent 可以将任务拆解为：

用户目标

查询订单并在满足条件时退款

Step 1：查询订单

query_order

Step 2：检查退款资格

check_refund_eligibility

Step 3：检查用户权限

check_permission

Step 4：Decision

是否满足退款条件？

全部满足

execute_refund

任一不满足

拒绝退款

Final Response

向用户返回最终执行结果

这里需要掌握三个概念：

- Goal：用户最终希望完成的目标。
- Plan：为实现目标而拆解的步骤。
- Step：计划中的具体执行动作。

面试重点：

Planning 不等于简单地连续调用多个 Tool，而是根据目标确定任务步骤及其依赖关系。

另外需要注意：不是所有 Agent 都有独立的 Planner 模块。有些 Agent 是通过 LLM 在每一轮动态决定下一步行动，实现隐式规划。

### 2. Decision Making：Agent 如何决定下一步？

这是今天最重要的知识点。

假设 Agent 已经查询到了订单：

```
{    "order_id": "ORD1001",    "status": "PAID",    "amount": 199,    "refund_status": "NOT_REFUNDED"}
```

接下来应该做什么？

可能有几种情况：

| 订单状态  | 下一步动作     |
| ----- | --------- |
| 已支付   | 继续检查退款资格  |
| 未支付   | 不允许退款     |
| 已退款   | 不允许重复退款   |
| 订单不存在 | 终止执行并返回错误 |

这就是 Decision Making。

Agent 根据当前 Observation，选择下一步行动。

这里需要特别区分两种决策：

第一种：LLM 决策

LLM 根据用户目标、上下文和工具描述，判断应该调用哪个工具。

例如：

```
LLM：
订单已经查询成功，
下一步需要检查退款资格。

Tool Call：
check_refund_eligibility
```

第二种：业务规则决策

由 Python 代码或业务系统执行明确的业务规则判断。

例如：

```
if order["status"] != "PAID":    return "ORDER_NOT_PAID"if not eligibility["eligible"]:    return "REFUND_NOT_ALLOWED"
```

对于电商支付场景，必须特别注意：

不能把关键业务安全规则完全交给 LLM 判断。

例如：

- 用户是否有权限退款。
- 订单是否已经支付。
- 是否允许重复退款。
- 退款金额是否超过原订单金额。

这些应该由可信的业务代码、权限系统或交易系统进行校验。

LLM 可以负责理解任务和提出下一步行动，但不能取代业务系统的最终安全校验。

### 3. Conditional Execution：条件分支执行

Planning 解决步骤拆解，Decision 解决下一步选择。

Conditional Execution 则是将决策结果转化为实际执行路径。

例如：

```
if order["status"] != "PAID":    return "ORDER_NOT_PAID"if not eligibility["eligible"]:    return "REFUND_NOT_ALLOWED"if not permission["allowed"]:    return "PERMISSION_DENIED"result = execute_refund(order["order_id"])
```

这里包含三个关键能力：

1. 根据条件决定是否继续执行。
2. 不满足条件时终止后续流程。
3. 满足全部条件时才执行退款。

需要理解一个重要原则：

高风险工具必须受到业务条件和权限校验的约束，不能仅凭 LLM 返回了 execute_refund 就直接执行。

### 4. Planning 与 Execution 的区别

这是面试中比较容易被问到的问题。

| 对比   | Planning   | Execution    |
| ---- | ---------- | ------------ |
| 核心职责 | 规划任务步骤     | 实际执行步骤       |
| 主要关注 | 下一步做什么     | 如何执行         |
| 典型行为 | 拆解任务、选择路径  | 调用 Tool      |
| 主要输入 | 用户目标、当前状态  | Tool Call、参数 |
| 主要输出 | 执行计划或下一步决策 | 工具执行结果       |

举例：

```
Planning：
1. 查询订单
2. 检查退款资格
3. 检查权限
4. 执行退款

Execution：
调用 query_order
获取订单信息

调用 check_refund_eligibility
获取退款资格

调用 check_permission
获取权限结果

调用 execute_refund
获取退款结果
```

两者不是完全独立的。

在动态 Agent 中，Planning 可以随着每次 Tool Execution 返回的 Observation 不断调整。

例如：

原计划是查询订单后检查退款资格，但查询发现订单已经退款，Agent 就应该终止原计划，而不是继续执行退款。

### 5. Planning 的常见类型

今天只需要认识两种，不深入复杂算法。

类型一：固定流程规划（Fixed Workflow）

提前定义好业务流程：

```
查询订单
   ↓
检查退款资格
   ↓
检查权限
   ↓
执行退款
```

优点：

- 流程清晰。
- 容易测试。
- 适合支付、退款等业务场景。

缺点：

- 灵活性有限。
- 流程变化需要修改代码或配置。

类型二：动态规划（Dynamic Planning）

LLM 根据当前任务和 Observation 动态选择下一步。

例如：

```
用户请求
   ↓
LLM 决定查询订单
   ↓
获取订单结果
   ↓
LLM 根据结果决定下一步
   ↓
继续调用工具或直接结束
```

优点：

- 灵活。
- 能处理不完全固定的任务。
- 能根据执行结果调整路径。

缺点：

- 决策存在不确定性。
- 更难测试。
- 可能产生不必要的工具调用。

今天先掌握两者的区别，后续再学习更复杂的 Workflow 和 Agent Planning。

## 三、今日编码实践：实现一个简单的 Planning & Decision Agent

今天不重新实现 Day 7 的 Agent Loop。

也不需要重写之前的 ToolExecutor、FakeLLM、State 等代码。

我们在现有代码基础上增加一个简单的业务决策流程。

### 1. 今日代码目标

实现一个简化的电商退款 Agent。

用户输入：

```
查询订单 ORD1001，
如果符合退款条件，就帮我退款。
```

预期执行流程：

```
User Input
    ↓
Agent
    ↓
query_order
    ↓
获取订单信息
    ↓
check_refund_eligibility
    ↓
检查退款资格
    ↓
check_permission
    ↓
检查用户权限
    ↓
Decision
    ↓
是否满足全部条件？
    ├── 是 → execute_refund
    │          ↓
    │       Final Answer
    │
    └── 否 → 终止执行
               ↓
            Final Answer
```

今天需要实现的关键能力：

- Agent 能够按照业务目标执行多个步骤。
- 能够根据工具返回结果进行判断。
- 能够根据判断结果决定是否执行下一步。
- 不满足业务条件时，不能调用退款工具。

### 2. 建议项目结构

沿用当前 GitHub 项目，不创建新项目。

```
ai-agent-testing/
│
├── src/
│   ├── agent/
│   │   ├── agent.py
│   │   ├── state.py
│   │   ├── llm_client.py
│   │   └── tool_executor.py
│   │
│   └── tools/
│       ├── order_tool.py
│       ├── refund_tool.py
│       └── permission_tool.py
│
└── tests/
    └── week02/
        └── test_agent_decision.py
```

今天尽量复用已有文件。

新增或调整的重点是：

| 文件                     | 今日任务                          |
| ---------------------- | ----------------------------- |
| agent.py               | 增加多步骤任务执行与条件判断                |
| state.py               | 保存订单信息、退款资格、权限结果              |
| llm_client.py          | 复用 Day 7 FakeLLM 接口，不必接真实 API |
| tool_executor.py       | 复用原有工具执行机制                    |
| test_agent_decision.py | 验证决策与条件分支                     |

不需要为了实现 Planning 而增加复杂的 Planner 类。

今天先用最简单的 Python 代码理解底层机制。

### 3. 核心编码任务：实现业务决策逻辑

下面是教学用的代码框架。

注意：这是一个简化的固定流程示例，目的是让你理解业务条件如何控制工具执行，并不是完整的动态 LLM Planner。

你需要自己补充关键逻辑。

```
class RefundAgent:    def __init__(self, tool_executor):        self.tool_executor = tool_executor    def run(self, order_id):        # Step 1: 查询订单        order = self.tool_executor.execute(            "query_order",            {"order_id": order_id}        )        # TODO 1: 判断订单是否存在        # TODO 2: 判断订单是否已经支付        # Step 2: 检查退款资格        eligibility = self.tool_executor.execute(            "check_refund_eligibility",            {"order_id": order_id}        )        # TODO 3: 判断是否符合退款条件        # Step 3: 检查用户权限        permission = self.tool_executor.execute(            "check_permission",            {"order_id": order_id}        )        # TODO 4: 判断用户是否有退款权限        # Step 4: 执行退款        result = self.tool_executor.execute(            "execute_refund",
```

你需要重点思考：

1. 如果订单不存在，是否应该继续检查退款资格？
2. 如果订单未支付，是否应该调用退款工具？
3. 如果退款资格检查失败，是否还需要检查权限？
4. 如果用户没有退款权限，是否允许执行退款？
5. 所有条件满足后，才能调用哪个工具？

重要： 这里的权限检查和退款资格检查必须来自可信工具结果，退款工具本身还应该再次进行必要的权限、金额、订单状态等交易校验。Agent 层的判断不能代替退款工具的安全校验。

### 4. 今日需要理解的一个重要问题：固定流程和动态决策

上面的 `RefundAgent` 是固定流程。

那么，Day 7 学习的 LLM Agent 能不能完成相同的事情？

可以。

例如：

```
LLM 第一次：
决定调用 query_order

Tool 返回：
订单已支付

LLM 第二次：
决定调用 check_refund_eligibility

Tool 返回：
符合退款条件

LLM 第三次：
决定调用 check_permission

Tool 返回：
用户有权限

LLM 第四次：
决定调用 execute_refund

Tool 返回：
退款成功

LLM 第五次：
生成最终回答
```

两种方式的区别：

| 固定流程 Agent    | 动态决策 Agent          |
| ------------- | ------------------- |
| Python 控制执行顺序 | LLM 参与选择下一步         |
| 业务路径预先定义      | 根据 Observation 动态调整 |
| 可预测性较高        | 灵活性较高               |
| 适合强业务约束流程     | 适合开放式复杂任务           |

今天不要求你把两种模式都实现。

先完成固定流程版本，建立 Planning 和 Decision 的基础认知。

之后再学习如何让 LLM 参与动态规划。

## 四、今日测试实践：验证 Decision 与 Conditional Execution

今天测试不是重点增加 Cases 数量。

重点是验证：

Agent 是否能够根据业务结果正确选择执行路径。

建议保留以下 5 个测试。

| 测试      | 验证的技术能力     |
| ------- | ----------- |
| 正常退款    | 所有条件满足，执行退款 |
| 订单未支付   | 正确阻断退款      |
| 不符合退款资格 | 正确阻断退款      |
| 用户无退款权限 | 正确阻断退款      |
| 订单不存在   | 提前终止流程      |

### 1. 测试重点

不要只验证最终返回结果。

还要验证工具调用情况。

例如：

正常退款：

```
assert result["status"] == "SUCCESS"assert tool_executor.call_count == 4assert "execute_refund" in tool_executor.called_tools
```

订单未支付：

```
assert result["error_code"] == "ORDER_NOT_PAID"assert "execute_refund" not in tool_executor.called_tools
```

用户没有退款权限：

```
assert result["error_code"] == "PERMISSION_DENIED"assert "execute_refund" not in tool_executor.called_tools
```

注意：以上断言假设工具执行器记录工具名称；具体返回结构根据你现有项目调整。

### 2. 今天需要重点验证的技术问题

第一：工具调用顺序

正常退款时，应该按照预期顺序执行：

```
expected_tools = [    "query_order",    "check_refund_eligibility",    "check_permission",    "execute_refund"]assert tool_executor.called_tools == expected_tools
```

第二：条件不满足时是否提前终止

例如订单未支付：

```
query_order
    ↓
发现订单未支付
    ↓
终止执行
```

不能继续执行：

```
check_refund_eligibility
check_permission
execute_refund
```

第三：是否存在不应该发生的工具调用

这是今天最重要的测试能力。

例如：

最终 Agent 返回：

```
退款失败，用户没有退款权限。
```

但是实际执行日志显示：

```
query_order
check_refund_eligibility
execute_refund
check_permission
```

虽然最终回复正确，但执行过程存在严重问题。

因为退款操作已经发生，权限检查却在退款之后。

所以，今天要记住：

Agent 的执行正确性，不仅取决于最终回答，还取决于中间执行路径是否符合预期。

## 五、今日问题分析：从测试工程师转向 Agent 测试工程师

今天重点思考下面三个问题。

### 问题 1：Planning 与 Decision 有什么区别？

用户要求：

> 查询订单，如果已经支付并且符合退款条件，就退款。

请分别说明：

- Agent 如何进行 Planning？
- Agent 如何进行 Decision？
- 两者之间有什么关系？

### 问题 2：如果 LLM 决定调用 execute_refund，但是订单实际没有支付，Agent 应该怎么处理？

请考虑：

- 是否可以直接执行 LLM 返回的 Tool Call？
- 应该在哪一层进行业务校验？
- 如果 LLM 多次要求执行退款，应该如何保证业务安全？

### 问题 3：固定流程 Agent 和动态决策 Agent，哪一种更适合电商支付业务？

请从以下角度分析：

- 灵活性。
- 可测试性。
- 执行稳定性。
- 业务安全性。

不要求回答唯一正确答案，重点是能够结合电商支付场景说明原因。

## 六、今日学习成果与验收标准

今天不要求开发完整的动态 Planning Agent。

重点是能够理解任务规划、决策和条件分支执行，并独立实现一个简单版本。

### Day 8 验收清单

学习进度

# 0/8

能够解释 Planning、Decision、Execution 的区别

能够画出电商退款 Agent 的任务执行流程

能够解释固定流程与动态决策的区别

独立实现一个简单的多步骤 RefundAgent

能够根据订单状态决定是否继续执行

能够根据退款资格和权限结果控制执行分支

使用 Pytest 验证正常退款及关键异常路径

能够分析错误决策、越权调用和不安全执行问题

可以在学习过程中逐项勾选。

### Review 评分标准

| 维度          | 分值  |
| ----------- | --- |
| 技术原理理解      | 30  |
| Python 编码能力 | 25  |
| 自动化测试能力     | 30  |
| 问题分析能力      | 15  |
| 总分          | 100 |

建议达到 80 分以上，并且不存在关键业务安全问题，才进入 Day 9。

特别是：不允许在权限检查失败、订单未支付或退款资格不满足的情况下执行退款。

## 七、今天的学习顺序

建议按照以下顺序完成，不要一开始就写代码。

| 步骤 | 学习任务                           | 建议时间  |
| -- | ------------------------------ | ----- |
| 1  | 理解 Planning、Decision、Execution | 35 分钟 |
| 2  | 自己画出退款 Agent 执行流程              | 20 分钟 |
| 3  | 理解固定流程与动态决策                    | 25 分钟 |
| 4  | 手写 RefundAgent                 | 60 分钟 |
| 5  | 编写 Fake Tool Executor 和 5 个测试  | 60 分钟 |
| 6  | 回答三个问题并整理知识点                   | 30 分钟 |

总计约 3–4 小时，实际时间根据编码进度调整。

### 今天暂时不学习的内容

为了控制学习难度，以下内容留到后续：

- LangGraph 的 StateGraph。
- ReAct Agent 的深入实现。
- 多 Agent 协作。
- 复杂 Planning 算法。
- DAG 工作流引擎。
- LLM 自动生成复杂执行计划。
- 多轮动态规划优化。

今天不需要增加新的框架，也不需要为了学习 Planning 重构 Day 7 的代码。

## 八、Day 8 作业提交要求

完成后，向我提交以下内容：

1\. 执行流程图

自己画出退款 Agent 的 Planning、Decision 和 Execution 流程。

2\. 核心代码

提交：

- `agent.py`
- `state.py`（如果有修改）
- `test_agent_decision.py`

3\. Pytest 执行结果

提供完整的测试结果，尤其是工具调用顺序和调用次数。

4\. 三个问题的回答

提交第五部分的三个问题答案。

我会按照之前的导师式 Review 方式逐项检查：

- 哪些知识真正理解了，哪些只是记住了概念。
- Planning 和 Decision 是否区分清楚。
- 业务条件是否真正控制了执行流程。
- 是否存在不合理的工具调用。
- Pytest 能否发现执行路径中的真实问题。
- 是否能够从测试工程师的角度分析 Agent 的决策风险。

## 九、Day 8 与 Day 9 的学习衔接

今天完成后，你的能力将从 Agent Execution 进一步扩展到 Agent Decision。

| 学习日   | 核心能力                | 需要回答的问题         |
| ----- | ------------------- | --------------- |
| Day 7 | Execution Loop      | Agent 如何执行？     |
| Day 8 | Planning & Decision | Agent 如何决定下一步？  |
| Day 9 | Agent Reliability   | Agent 如何保证执行可靠？ |

Day 9 将重点学习 Agent Reliability，包括：

1. Tool Call 重复执行问题。
2. Retry 与超时处理。
3. 幂等性（Idempotency）。
4. 执行失败后的恢复机制。
5. 如何验证 Agent 的可靠性。

这些内容与电商支付、退款业务非常相关，也是 Agent 测试岗位值得重点掌握的技术能力。

## Day 8 今日核心目标

从 Agent 会执行，提升到 Agent 会根据目标和业务条件选择正确的执行路径。

今天最重要的不是写多少代码，而是建立一个正确的架构认知：

- Planning：规划要做哪些事情。
- Decision：决定下一步做什么。
- Execution：实际执行操作。
- Validation：确保执行符合业务规则和安全约束。

今日学习任务已发布

导师要求： 今天继续坚持少而精的学习方式。不要让 AI 直接生成完整代码，先自己写，遇到困难再提交代码片段和思路。我会像 Day 7 一样进行严格 Review，合格后再进入 Day 9。

如果你希望明天固定时间继续学习，可以设置一个 Day 8 作业提交提醒。

📚明天提醒提交 Day 8 作业轻点设置