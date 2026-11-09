已整理成一份可以在后续对话中继续使用的 《AI Agent 测试学习档案》。它记录了你的学习目标、已完成内容、代码基础、当前能力、学习偏好和下一阶段任务。

# AI Agent 测试学习档案

**档案更新时间：2026年11月8日**

## 一、学习目标

- **核心目标：** 尽快达到 AI Agent 测试岗位的面试要求。
- **学习方向：** 以 Python + Pytest 为基础，结合电商支付 Agent 项目进行实战。
- **学习策略：** 第一阶段优先达到面试水平，第二阶段再深入研究复杂 Agent 技术。
- **学习原则：** 少而精，优先掌握高价值知识点和核心测试场景，不追求过度细节。

## 二、学习方式与要求

希望采用导师式教学和严格代码评审模式：

1. 每天明确学习目标和核心知识点。
2. 使用电商支付 Agent 作为贯穿案例。
3. 每天提供简化的 Agent 代码框架。
4. 重点测试场景控制数量，优先覆盖高价值风险。
5. 自己编写 Python + Pytest 代码并提交测试结果。
6. 导师逐项评审代码、测试覆盖和业务逻辑。
7. 评审给出分数、问题分析和修改建议。
8. 达到验收标准后再进入下一天。

特别要求：代码必须控制复杂度，优先保证自己能够理解、解释和手写，不要过度依赖 AI 生成代码。

## 三、学习进度

| 阶段    | 学习内容                                 | 当前状态         |
| ----- | ------------------------------------ | ------------ |
| Day 1 | Agent 测试基础                           | 已学习          |
| Day 2 | 前期基础内容                               | 已完成（具体内容待补充） |
| Day 3 | Prompt Engineering 与 Prompt Testing  | 已学习          |
| Day 4 | 最小 Agent 执行框架、工具执行、权限和业务校验           | 已完成          |
| Day 5 | LLM Tool Calling、Tool Schema、FakeLLM | 已通过          |
| Day 6 | Agent tool calling 自动化测试                  | 待开始          |

## 四、Day 3：Prompt Engineering 与 Prompt Testing

已学习的重点：

- System Prompt、User Prompt、Context 的区别。
- 如何通过 Prompt 约束业务行为。
- 如何测试 Agent 是否遵守业务规则。
- Prompt 测试数据集设计。
- 用户诱导、错误信息和越权请求的鲁棒性测试。

典型场景：

用户声称订单已经支付，要求直接退款，但 Agent 不能盲目信任用户输入，仍然需要查询订单、校验退款条件和用户权限。

## 五、Day 4：最小 Agent 执行框架

已接触的核心模块：

- Agent
- AgentState
- OrderTool
- PermissionTool
- RefundTool

已理解的核心执行流程：

1. 接收用户输入。
2. Agent 组织上下文并决定执行工具。
3. 检查工具是否在允许列表中。
4. 校验工具参数。
5. 执行 Python Tool。
6. 将工具结果记录为 Observation。
7. 根据执行结果返回用户。

重点理解的安全原则：

- 工具必须在允许列表中。
- Schema 参数校验不能代替业务校验。
- 退款工具必须独立校验订单归属、支付状态、退款状态和金额。
- 不能完全信任 LLM 或前置权限检查的结果。

学习反馈：Day 4 代码难度较高，曾借助 AI 工具生成部分代码。目前基本理解，但还不能完全独立手写。因此后续应继续使用简化框架，避免增加不必要的抽象和代码量。

## 六、Day 5：LLM Tool Calling

**学习状态：正式通过，90/100。**

本阶段重点掌握：

- LLM 如何根据用户意图选择工具。
- Tool Schema 与 Python Tool 的区别。
- LLM 返回工具名称和参数。
- Agent 校验工具名称与参数。
- Agent 执行工具并生成 Observation。
- 将工具结果返回 LLM，形成 Tool Calling Loop。
- 使用 FakeLLM 模拟 LLM 行为，控制工具调用过程。

当前项目中的核心工具：

- query_order
- permission_check
- execute_refund

已完成的 8 个测试场景：

| 编号   | 测试场景           | 结果   |
| ---- | -------------- | ---- |
| TC01 | 查询订单，选择正确工具和参数 | PASS |
| TC02 | 权限检查和退款工具调用正确  | PASS |
| TC03 | 非订单所有者不能退款     | PASS |
| TC04 | 未支付订单不能退款      | PASS |
| TC05 | 查询退款状态不能误触发退款  | PASS |
| TC06 | 非法工具名称不能执行     | PASS |
| TC07 | 异常订单金额不能退款     | PASS |
| TC08 | 退款工具独立拒绝他人订单   | PASS |

最新测试结果：

`8 passed in 0.05s`

最新代码已更新至 GitHub，并完成了相关代码复查。

Day 5 已修复的问题：

- Permission Check 成功与失败时的 Observation 记录逻辑。
- Permission Check Schema 中多余的 amount 参数。
- Execute Refund Schema 参数精简。

另有一项测试命名优化建议：TC04 的实际行为是退款工具被调用后拒绝未支付订单，而不是完全不调用退款工具。

## 七、当前代码项目

GitHub 仓库：

[https://github.com/chunrong50/ai-agent-testing](https://github.com/chunrong50/ai-agent-testing)

主要代码结构：

```
ai-agent-testing/
├── src/
│   ├── agent/
│   │   ├── agent.py
│   │   ├── state.py
│   │   └── llm_agent.py
│   ├── tools/
│   │   ├── order_tool.py
│   │   ├── permission_tool.py
│   │   └── refund_tool.py
│   └── schemas/
│       └── tool_schemas.py
└── tests/
    └── week01/
        └── test_tool_calling.py
```

当前技术栈：

- Python
- Pytest
- FakeLLM
- Tool Calling
- JSON Schema 风格的工具定义
- GitHub 代码管理

## 八、当前能力评估

**已经具备的能力：**

1. 能够解释最小 Agent 的基本执行流程。
2. 能够区分 LLM、Agent、Tool 和 Observation。
3. 能够理解 Tool Schema 的作用。
4. 能够理解 LLM 选择工具、Agent 执行工具的基本机制。
5. 能够使用 FakeLLM 编写工具调用测试。
6. 能够围绕支付和退款业务设计核心测试场景。
7. 能够识别权限校验、参数校验和后端业务校验的区别。

**目前需要继续加强的能力：**

1. 独立手写 Agent 核心代码的能力。
2. 对 Tool Calling Loop 的执行机制理解。
3. 对异常、失败和边界情况的系统化测试能力。
4. 从测试结果中定位 Agent 执行链路问题的能力。
5. 将测试场景转化为面试中清晰、准确的表达。

注意：目前的学习成果主要来自简化框架和 FakeLLM 测试，不能等同于已经掌握真实大模型 API、生产级 Agent 架构或完整自动化测试体系。

## 九、下一阶段学习计划

### Day 6：Agent 执行可靠性测试

建议重点学习：

- 工具执行异常时 Agent 如何处理。
- 工具返回失败结果时是否正确终止。
- LLM 连续请求工具时是否有最大调用次数限制。
- 工具执行失败后是否会错误地继续退款。
- Agent 是否能正确记录失败 Observation 和最终状态。

保持少而精，建议设计 4～6 个核心测试用例。

### Day 7～Day 10

根据 Day 6 的实际学习结果，再逐步安排后续主题。不要提前堆叠过多复杂知识点。

## 十、后续教学必须遵守的原则

1. 继续使用当前电商支付 Agent 案例。
2. 尽量沿用现有代码结构，不轻易重构。
3. 每天先讲清楚原理，再提供最小代码框架。
4. 测试用例少而精，优先面试高频场景。
5. 代码难度必须符合当前实际水平。
6. 代码评审要严格，不因为测试通过就默认代码完全正确。
7. 每天保留学习进度、测试结果、评分和待改进问题。
8. 达到验收标准后才能进入下一阶段。

**当前学习节点：Day 5 正式通过，下一步从 Day 6 开始。**

这份档案可以作为后续学习的基准。之后你只需要说“继续 Day 6”，我就按这份档案的学习目标、难度和教学方式继续，不需要重新介绍前面的进度。

