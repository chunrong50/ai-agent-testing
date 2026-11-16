根据目前的学习记录、最近的代码评审和 Day 13 最终验收结果，整理了最新版本的《AI Agent 测试学习档案》。

这份档案可以作为后续新对话继续学习的上下文，避免重复学习已经通过的内容。

# AI Agent 测试学习档案

**档案日期：2026 年 11 月 16 日**\
**当前学习进度：Day 13 已通过，准备进入 Day 14**

---

## 一、学习目标

### 第一阶段：达到初级 AI Agent 测试工程师面试水平

目标是在较短时间内掌握 AI Agent 测试的核心知识，能够：

1. 解释 Agent 的基本架构和执行机制。
2. 理解 LLM、Prompt、Tool Calling、Memory、Planning 等核心概念。
3. 能够使用 Python + Pytest 编写 Agent 自动化测试。
4. 能够设计 Agent 核心业务测试场景。
5. 能够识别 Agent 执行过程中的异常和安全问题。
6. 能够结合实际项目回答 AI Agent 测试工程师面试问题。

### 第二阶段：深入学习

第一阶段达到面试要求后，再深入学习：

- 多 Agent 协作
- 复杂 Planning
- Memory 优化
- Agent 评估体系
- RAG 测试
- Agent 性能及可靠性测试

当前不提前扩展第二阶段内容。

---

## 二、学习方式及原则

采用导师式学习 + 严格代码评审。

每个 Day 包含：

1. 明确学习目标。
2. 学习核心知识点。
3. 结合电商支付 Agent 理解业务场景。
4. 编写 Python + Pytest 测试代码。
5. 提交代码及 pytest 执行结果。
6. 逐项代码评审。
7. 给出评分、问题分析和修改建议。
8. 达到验收标准后才能进入下一 Day。

### 学习原则

- 少而精，不追求大量测试用例。
- 优先掌握面试高频知识。
- 尽量自己理解和编写代码，不依赖 AI 完全生成。
- 不为了代码复杂度而增加不必要的架构。
- 重点是理解 Agent 的底层执行机制及测试方法。
- 每个知识点既要理解，也要能够解释和设计测试。

---

## 三、项目实践环境

GitHub 项目：

[https://github.com/chunrong50/ai-agent-testing](https://github.com/chunrong50/ai-agent-testing)

主要目录：

```
ai-agent-testing/
├── src/
│   ├── agent/
│   └── tools/
│
├── tests/
│   ├── week01/
│   └── week02/
│
└── docs/
```

技术栈：

- Python
- Pytest
- FakeLLM
- Agent Tool Calling
- AgentState
- Planning / Step / Plan
- pytest 自动化测试

业务场景：电商支付 Agent。

典型业务流程：

查询订单 → 权限校验 → 退款资格校验 → 执行退款。

---

## 四、已完成的学习内容

### Day 1–Day 4：Agent 基础及执行框架

已学习内容包括：

- Agent 基本架构。
- LLM 与 Agent 的关系。
- Prompt 基础。
- Tool 基础。
- Agent 最小执行框架。
- AgentState。
- 订单查询、权限校验、退款工具。
- Agent 执行链路。

Day 4 的重点收获：

能够解释：

用户输入 → Agent → LLM → Tool Call → Tool 执行 → Observation → LLM → 最终响应。

同时理解工具白名单、Schema 校验及业务层二次校验的重要性。

Day 4 曾经遇到代码实现困难，后来采用简化框架继续学习。目前已经基本理解执行机制，不要求独立实现复杂 Agent 框架。

### Day 5：LLM Tool Calling

**评分：90/100**

\<badge color="success">已通过\</badge>

掌握内容：

- LLM 如何选择工具。
- Tool Schema 的作用。
- Tool Call 参数传递。
- Agent 如何解析并执行工具。
- 工具白名单校验。
- 参数 Schema 校验。
- 业务层安全校验。
- FakeLLM 控制工具调用过程。

实际测试结果：

`test_tool_calling.py`：8 passed。

已修复的问题：

- Observation 重复记录。
- permission_check Schema 多余参数。
- 退款工具后端业务校验。

还理解了一个重要区别：

即使 Agent 调用了退款工具，退款工具本身仍必须独立执行业务校验，阻止未支付订单退款。

### Day 6–Day 8：Agent 执行可靠性相关学习

已进入 Agent 执行过程、异常处理、状态管理和测试框架的学习阶段。

Day 8 已进行阶段性验收。

具体各日的独立评分及全部测试明细暂未完整记录，不补造历史成绩。

### Day 9：AgentState 与状态隔离

已完成相关学习和代码练习。

重点：

- AgentState 的状态管理。
- 不同用户之间的状态隔离。
- Mutable 对象及默认值问题。
- 测试不同 AgentState 实例之间是否相互影响。

### Day 10–Day 12：Agent 测试框架及执行过程

已完成相应阶段的学习。

Day 11 曾重构 Agent 测试，重点关注：

- 测试代码结构。
- 状态隔离。
- Agent 执行过程的可测试性。

Day 12 的具体独立验收细节尚未完整归档。

---

## 五、Day 13：Planning Agent

**最终状态：正式通过**

Day 13 是目前学习中比较重要的一个阶段。

重点学习 LLM Plan Agent 的执行机制。

### 1. Plan 生成

LLM 在执行前生成 Plan。

Plan 包含多个 Step，每个 Step 描述一个需要执行的任务。

### 2. Step 执行

Agent 根据 Plan 执行 Step。

当前学习的实现采用先生成 Plan，再依次执行 Step 的方式。

### 3. Observation

每个 Step 执行后：

- 产生执行结果。
- Observation 保存到 AgentState。
- Observation 也会作为 Message Content 传递给 LLM。

### 4. 执行过程中的重要区别

当前 `LLMPlanAgent` 的实现：

- Plan 在执行前生成。
- Step 执行后保存 Observation。
- 执行完一个 Step 后，不会自动再次调用 LLM 进行决策。
- 不能将这种实现误认为每一步都由 LLM 重新规划。

### 5. Step 状态及依赖管理

掌握的状态包括：

- pending
- running
- completed
- failed

理解 Step 依赖关系以及 `get_ready_steps()` 的作用。

重要知识点：

`get_ready_steps()` 负责识别满足依赖条件的 Step。

Engine 负责控制是否继续执行。

即使某个 Step 的依赖满足，如果 Engine 已经进入 failed 终止流程，也不会继续执行后续 Step。

### 6. Plan 替换机制

理解 `set_plan()` 的核心概念：

```
self.plan = new_plan
```

如果采用直接赋值：

- 新 Plan 替换旧 Plan。
- 旧 Plan 中的 Step 状态不会自动迁移到新 Plan。
- 如果需要保留 completed 状态，需要额外实现状态合并或恢复逻辑。

### 7. Day 13 最终验收

**评分：85/100**

\<badge color="success">正式通过\</badge>

主要掌握：

- Plan 生成与执行。
- Step 状态管理。
- Observation 记录与传递。
- Step 依赖调度。
- Engine 失败终止。
- Plan 替换与状态保留的区别。

仍需在后续学习中进一步巩固：

- get_ready_steps 与 Engine 控制的区别。
- Plan 替换后的状态恢复。
- Replanning 与原 Plan 的关系。

---

## 六、当前能力评估

目前已经具备：

1. 能够解释 Agent 的基本执行架构。
2. 能够理解 LLM 与 Tool Calling 的关系。
3. 能够使用 FakeLLM 控制测试过程。
4. 能够使用 Pytest 验证 Agent 执行行为。
5. 能够理解 Observation 和 AgentState。
6. 能够理解 Plan、Step 及依赖关系。
7. 能够分析 Agent 异常终止和执行状态。

目前需要继续加强：

- 独立编写 Agent 测试代码的能力。
- 对 Agent 底层执行流程的理解。
- 对异常恢复和状态一致性的测试设计。
- 面试中将技术原理转化成简洁、准确的语言。

---

## 七、下一阶段学习计划

### Day 14：Agent 执行状态与异常恢复

重点学习：

- Agent 执行状态管理。
- Step 执行异常。
- 执行中断与恢复。
- 状态一致性。
- 异常恢复测试。

重点不是增加大量代码，而是理解异常发生后 Agent 的状态是否正确。

### Day 15–Day 17

逐步学习：

- Agent Memory。
- 历史消息管理。
- Context 管理。
- Memory 测试。
- 上下文污染及信息隔离。

### Day 18–Day 20

逐步学习：

- Agent 安全测试。
- Prompt Injection。
- Tool 权限控制。
- 越权操作。
- Agent 业务规则遵循性。

### Day 21–Day 25

逐步学习：

- Agent 评估体系。
- LLM 输出质量评估。
- 稳定性测试。
- Agent 端到端测试。
- 测试报告与面试项目总结。

以上是后续建议安排，实际内容根据学习进度调整。

---

## 八、后续导师必须遵守的要求

1. 每次开始新 Day，先说明学习目标及面试价值。
2. 先讲原理，再做少量有价值的练习。
3. 不要直接提供完整代码让学习者复制。
4. 优先让学习者自己分析和编写。
5. 对代码逐项评审，不能只看 pytest 是否通过。
6. 每个 Day 都要有明确的通过标准。
7. 未达到验收标准，不直接进入下一 Day。
8. 不重复已经掌握的基础内容。
9. 遇到复杂实现时，优先简化框架。
10. 最终目标是具备初级 AI Agent 测试工程师的面试能力。

---

## 九、当前学习状态

| 项目    | 当前状态            |
| ----- | --------------- |
| 学习阶段  | 第一阶段：面试准备       |
| 已学习进度 | Day 13          |
| 最近通过  | Day 13          |
| 下一课   | Day 14          |
| 主要技术  | Python + Pytest |
| 实践项目  | 电商支付 Agent      |
| 学习方式  | 导师教学 + 代码评审     |
| 学习重点  | Agent 执行机制与测试设计 |

**下一次学习直接从 Day 14 开始，不需要重新学习 Day 1–Day 13。**

**档案更新完成。**

建议后续继续使用这份档案作为学习基准。Day 14 我会继续按照之前的要求：先讲原理、再做少量练习、最后严格验收。