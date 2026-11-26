已根据截至 **2026 年 11 月 17 日 Day 15 学习结束**的记录，更新你的 AI Agent 测试学习档案。

这次重点更新了 Day 13、Day 14、Day 15 的学习进度、知识掌握情况，以及下一阶段学习安排。没有完整记录的成绩不会擅自补充。

# AI Agent 测试工程师学习档案

**档案版本：V3.0**\
**更新日期：2026 年 11 月 17 日**\
**当前学习进度：Day 15 已通过，准备进入 Day 16**

---

## 一、学习目标

### 第一阶段：达到 AI Agent 测试工程师面试水平

目标是在较短时间内掌握 AI Agent 测试的核心知识，能够：

1. 理解 Agent 基本架构和执行机制。
2. 理解 LLM、Prompt、Tool Calling、Memory、Planning 等核心概念。
3. 使用 Python + Pytest 编写 Agent 自动化测试。
4. 设计电商支付 Agent 的核心业务测试场景。
5. 理解 Agent 执行过程中的状态管理、异常处理和安全问题。
6. 能够结合实际项目回答 AI Agent 测试工程师面试问题。

### 第二阶段：深入学习

第一阶段达到面试要求后，再深入学习：

- 多 Agent 协作
- 复杂 Planning
- Memory 优化
- RAG 测试
- LLM Judge
- Agent 性能和可靠性测试

当前优先完成第一阶段，不提前扩展复杂内容。

---

## 二、学习方式及原则

采用导师式教学 + 严格代码评审。

每个 Day 包含：

1. 明确学习目标。
2. 学习核心知识点。
3. 结合电商支付 Agent 理解业务场景。
4. 完成少量有价值的 Python + Pytest 练习。
5. 提交代码及测试结果。
6. 逐项代码评审。
7. 给出评分、问题分析和修改建议。
8. 达到验收标准后进入下一 Day。

### 必须遵守的学习原则

- 少而精，不追求大量测试用例。
- 优先掌握面试高频知识。
- 重点理解 Agent 底层执行机制。
- 不为了测试覆盖率而盲目增加 Case。
- 不为了代码复杂度而增加不必要的架构。
- 优先使用简单、容易理解的代码框架。
- 先理解原理，再自己动手编写代码。
- 不要求独立实现复杂 Agent 框架。
- 不能只看 pytest 是否通过，还要检查测试逻辑是否正确。

---

## 三、项目实践环境

GitHub 项目：

[https://github.com/chunrong50/ai-agent-testing](https://github.com/chunrong50/ai-agent-testing)

技术栈：

- Python
- Pytest
- FakeLLM
- Agent Tool Calling
- AgentState
- Planning / Step / Plan
- Memory / Context

业务场景：电商支付 Agent。

典型业务流程：

查询订单 → 权限校验 → 退款资格校验 → 执行退款。

---

## 四、已完成的学习内容

### Day 1：LLM 基础与 API 测试

**状态：通过**

评分：88/100

主要学习：

- AI、LLM 基本概念。
- LLM 幻觉。
- Temperature。
- LLM Client。
- FakeModel、SpyModel。
- Pytest 自动化测试。

测试结果：14 passed。

### Day 2：Token、Tokenizer 与 Context Window

**状态：通过**

评分：89/100

主要学习：

- Token 与字符的区别。
- Tokenizer。
- tiktoken。
- Context Window 容量计算。
- Token 边界测试。
- FakeTokenCounter。

测试结果：43 passed。

### Day 3：Prompt Engineering 与 Prompt 测试

**状态：通过**

正式评分：80/100\
补充练习评分：86/100

主要学习：

- System Prompt、User Prompt、Context。
- 业务约束 Prompt。
- Prompt 静态测试。
- 正向、反向、边界和对抗测试。
- Prompt 测试数据集。
- 退款业务安全规则。

### Day 4：Agent 架构与运行机制

**状态：已完成学习**

主要学习：

- Agent 最小执行框架。
- AgentState。
- LLM 与 Agent 的关系。
- Tool 执行机制。
- Observation。
- 订单查询、权限校验、退款工具。
- 工具白名单。
- Schema 校验。
- 业务层二次校验。

关键执行链路：

用户输入 → Agent → LLM → Tool Call → Tool 执行 → Observation → LLM → 最终响应。

学习反馈：

Day 4 代码曾经有一定难度，借助 AI 工具完成部分代码。目前基本理解执行机制，但独立实现复杂框架仍有一定困难。

后续采用简化代码框架，不要求重复实现复杂代码。

### Day 5：LLM Tool Calling

**状态：通过**

评分：90/100

主要学习：

- LLM 如何选择工具。
- Tool Schema。
- Tool Call 参数传递。
- Agent 如何解析和执行工具。
- 工具白名单。
- 参数 Schema 校验。
- 业务层安全校验。
- FakeLLM 控制工具调用。

测试结果：

`test_tool_calling.py`：8 passed。

重要收获：

即使 Agent 调用了退款工具，退款工具本身仍然必须执行独立的业务校验。

### Day 6–Day 8：Agent 执行可靠性

**状态：已进入并完成阶段性学习，独立验收明细未完整归档**

主要学习方向：

- Agent 执行过程。
- 异常处理。
- 状态管理。
- 执行终止。
- 测试框架相关实践。

### Day 9：AgentState 与状态隔离

**状态：已完成学习**

主要学习：

- AgentState 状态管理。
- 不同用户之间的状态隔离。
- Mutable 对象。
- 默认值问题。
- 不同 AgentState 实例之间是否相互影响。

### Day 10–Day 12：Agent 测试框架及执行过程

**状态：已完成相应阶段学习**

主要学习：

- Agent 测试代码结构。
- 状态隔离。
- Agent 执行链路。
- 测试代码重构。
- 执行过程的可测试性。

独立评分和完整测试明细暂未归档。

---

## 五、Day 13：Planning Agent

**状态：正式通过**

评分：85/100

这是一个重要的学习阶段。

### 1. Plan 生成

LLM 在执行前生成 Plan。

Plan 包含多个 Step，每个 Step 描述一个需要执行的任务。

### 2. Step 执行

Agent 根据 Plan 依次执行 Step。

当前学习的实现采用先生成 Plan，再依次执行的方式。

### 3. Observation

每个 Step 执行后：

- 产生执行结果。
- Observation 保存到 AgentState。
- Observation 作为 Message Content 传递给 LLM。

### 4. 当前 LLMPlanAgent 的执行机制

- Plan 在执行前生成。
- Step 执行后保存 Observation。
- 执行完一个 Step 后，不会自动再次调用 LLM 进行决策。
- 不能将这种实现误认为每一步都由 LLM 重新规划。

### 5. Step 状态管理

掌握：

- pending
- running
- completed
- failed

理解 Step 依赖关系和 `get_ready_steps()` 的作用。

重要区别：

`get_ready_steps()` 负责识别满足依赖条件的 Step。

Engine 负责控制是否继续执行。

### 6. Plan 替换

理解 `set_plan()` 的核心机制：

```
self.plan = new_plan
```

直接赋值会替换旧 Plan，旧 Plan 的 Step 状态不会自动迁移到新 Plan。

### 7. Day 13 验收

评分：85/100。

已掌握：

- Plan 生成与执行。
- Step 状态管理。
- Observation 记录与传递。
- Step 依赖调度。
- Engine 失败终止。
- Plan 替换与状态保留的区别。

后续需要继续巩固：

- get_ready_steps 与 Engine 控制的区别。
- Plan 替换后的状态恢复。
- Replanning 与原 Plan 的关系。

---

## 六、Day 14：Agent 执行状态与异常恢复

**状态：已开始学习，独立验收记录待补充**

Day 14 属于 Agent 执行机制的延伸阶段。

后续学习重点：

- Agent 执行状态管理。
- Step 执行异常。
- 执行中断与恢复。
- 状态一致性。
- 异常恢复测试。

目前不补造 Day 14 的独立成绩和通过结论。

---

## 七、Day 15：Agent Memory 与 Context 管理

**状态：正式通过**

### 1. Observation 传递

理解第二次调用 LLM 时，Agent 会将之前的 Observation 作为消息传递给 LLM。

核心机制：

Tool 执行结果 → Observation → Message → 下一次 LLM 调用。

### 2. Memory 写入

Memory 用于保存历史交互信息和结构化上下文。

理解工具执行结果如何写入 Memory。

### 3. 业务数据时效性

重要原则：

Memory 中的业务数据不一定是最新的。

订单状态、支付状态等具有时效性的数据，应该以业务系统最新查询结果为准。

需要时重新调用 `query_order`。

### 4. Context 筛选

不应该将所有历史消息无差别传递给 LLM。

应该保留与当前任务相关的信息，例如：

- order_id
- user_id
- 与当前任务相关的历史操作

过滤无关内容，例如天气、Python 等历史问题。

### 5. Memory 更新

Agent 应根据最新工具执行结果更新 Memory，避免继续使用过期数据。

### 6. previous_result 管理

理解：

`previous_result` 只保存最近一次工具执行结果。

例如：

```
memory.context["previous_result"] = tool_result
```

每次工具执行后更新。

如果需要保存多个工具的执行结果，可以在 `memory.context` 中增加不同字段：

```
memory.context = {
    "query_order": {
        "status": "success",
        "order_status": "paid"
    },
    "execute_refund": {
        "status": "success",
        "refund_id": "REF001"
    }
}
```

关键原则：

- Memory 中保存的工具结果必须与实际工具执行结果一致。
- 不应由 Agent 或 LLM 擅自修改工具返回状态。
- `success` 表示工具执行成功，不一定表示业务操作成功。
- 需要区分工具执行状态与业务状态。

### 7. Day 15 验收结果

**正式通过。**

本次完成的知识检查：

| 检查项目           | 结果 |
| -------------- | -- |
| Observation 传递 | 通过 |
| Memory 写入      | 通过 |
| 业务数据时效性        | 通过 |
| Context 信息筛选   | 通过 |
| Memory 更新      | 通过 |
| 多工具结果管理        | 通过 |

Day 15 不要求继续扩展大量 Case，也不要求实现复杂 Memory 架构。

---

## 八、当前能力评估

目前已经具备：

1. 理解 Agent 基本执行架构。
2. 理解 LLM 与 Tool Calling 的关系。
3. 能够使用 FakeLLM 控制 Agent 测试过程。
4. 能够使用 Pytest 验证 Agent 执行行为。
5. 理解 Observation 和 AgentState。
6. 理解 Plan、Step 和依赖关系。
7. 理解 Agent 执行状态及失败终止。
8. 理解 Memory 写入、更新和读取。
9. 理解 Context 筛选和业务数据时效性。
10. 能够分析 Agent 执行过程中的状态传递。

目前需要继续加强：

- 独立编写 Agent 测试代码。
- 对 Agent 底层执行流程的理解。
- Memory 与 Context 的区别。
- 面试中将技术原理转化为简洁、准确的语言。

---

## 九、下一阶段学习计划

### Day 16：Memory 与 Context 管理机制

重点学习：

- 历史消息管理。
- 结构化业务数据。
- 当前任务上下文。
- Memory 与 Context 的区别。
- Memory 如何参与 LLM 调用。

重点是理解机制，不扩展复杂架构。

### Day 17–Day 18

逐步学习：

- Memory 相关测试。
- 历史信息管理。
- 上下文污染及信息隔离。
- Agent 上下文一致性。

### Day 19–Day 21

逐步学习：

- Agent 安全测试。
- Prompt Injection。
- Tool 权限控制。
- 越权操作。
- Agent 业务规则遵循性。

### Day 22–Day 25

逐步学习：

- Agent 评估体系。
- LLM 输出质量评估。
- 稳定性测试。
- Agent 端到端测试。
- 测试报告与面试项目总结。

后续安排根据实际学习进度调整。

---

## 十、后续导师必须遵守的要求

1. 每次开始新 Day，先说明学习目标及面试价值。
2. 先讲原理，再做少量有价值的练习。
3. 不直接提供完整代码让学习者复制。
4. 优先让学习者自己分析和编写代码。
5. 对代码逐项评审，不能只看 pytest 是否通过。
6. 每个 Day 都要有明确的通过标准。
7. 未达到验收标准，不直接进入下一 Day。
8. 不重复已经掌握的基础知识。
9. 遇到复杂实现时，优先简化框架。
10. 不要为了 Case 覆盖率盲目扩展测试场景。
11. 优先理解 Agent 核心机制和执行链路。
12. 第一阶段以达到初级 AI Agent 测试工程师面试水平为目标。

---

## 十一、当前学习状态

| 项目    | 当前状态                   |
| ----- | ---------------------- |
| 学习阶段  | 第一阶段：面试准备              |
| 已完成学习 | Day 15                 |
| 最近通过  | Day 15                 |
| 下一课   | Day 16                 |
| 主要技术  | Python + Pytest        |
| 实践项目  | 电商支付 Agent             |
| 学习方式  | 导师教学 + 严格代码评审          |
| 当前重点  | Agent Memory 与 Context |

**下一次学习直接从 Day 16 开始，不需要重新学习 Day 1–Day 15。**

档案版本：V3.0\
更新日期：2026 年 11 月 17 日

**当前进度：Day 15 已正式通过。**

下一次直接开始 Day 16。我会继续坚持少而精的原则，重点讲清楚 Memory、Context 和历史消息管理机制，不再为了增加 Case 数量而扩展不必要的异常场景。