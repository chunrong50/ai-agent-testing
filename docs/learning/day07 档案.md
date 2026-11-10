# AI Agent 测试学习档案

**档案日期：2026 年 11 月 10 日**

## 一、学习目标

### 第一阶段：面试能力
目标是在约一个月内，达到初级 AI Agent 测试工程师的面试要求。

重点是能够：
- 解释 Agent 的基本架构和执行机制。
- 理解 LLM、Prompt、Tool Calling、Observation、State 等核心概念。
- 使用 Python 实现简单 Agent。
- 使用 Pytest 对 Agent 核心功能进行自动化测试。
- 识别并测试 Agent 的关键风险和异常场景。
- 能够独立讲解项目代码、测试方案和问题定位过程。

### 第二阶段：项目交付能力
在第一阶段基础上继续深入，逐步具备：
- 复杂 Agent 架构测试能力。
- RAG、Memory、Workflow、Multi-Agent 测试能力。
- Agent 自动化测试框架设计能力。
- LLM Judge、质量评估和 Trace 分析能力。
- 性能、安全、稳定性测试能力。
- 完整 AI Agent 测试项目的设计与交付能力。

## 二、个人技术背景

- 软件测试工作经验：10 年以上。
- 编程语言：Python。
- 自动化测试框架：Pytest。
- 业务领域：电商、支付。
- 学习投入：可以全职投入。
- 当前基础：具备传统软件测试、自动化测试和业务测试经验。

学习方式：
- 少而精，优先学习高价值知识。
- 以电商支付 Agent 为实践项目。
- 重点学习 Agent 技术原理、架构、Python 实现和测试方法。
- 不以大量设计 Test Cases 作为主要学习目标。
- 代码必须尽量简单，能够理解、解释，逐步达到独立手写。
- 采用导师式教学和严格代码 Review。
- 每个阶段设置明确的学习目标和验收标准。

## 三、实践项目

GitHub 仓库：

https://github.com/chunrong50/ai-agent-testing

主要目录：

- `src/agent/`：Agent 核心实现
- `src/tools/`：业务工具实现
- `tests/week01/`：自动化测试
- `docs/`：学习文档

开发环境记录：

- macOS
- Python 3.9.1
- Pytest 8.4.2
- 虚拟环境：`.venv`

项目业务场景：电商支付 Agent，涉及订单查询、权限校验、退款资格校验和退款执行。

## 四、已完成学习内容

### Day 1–3：基础知识与 Prompt

已涉及：
- LLM 与 Agent 的基本概念。
- Agent 的基本工作方式。
- System Prompt、User Prompt、Context 的区别。
- 业务约束 Prompt。
- Prompt 遵循性和鲁棒性测试。
- 用户诱导、错误信息和越权请求的处理。

Day 3 的典型业务场景：

用户声称订单已经支付，并直接要求退款。Agent 不能仅依据用户说法执行退款，而应该查询订单、验证退款条件并进行权限校验。

注：Day 2 的独立学习记录仍需进一步核对，不将未核实内容标记为已完成。

### Day 4：最小 Agent 执行框架

已完成基本实现和学习。

涉及：
- Agent 的基本结构。
- LLM 与 Agent 的交互。
- Tool Schema。
- 工具白名单。
- 参数校验。
- Tool Executor。
- Observation。
- 权限检查。
- 业务层校验。

已经能够理解基本执行链路：

用户输入 → Agent → LLM → Tool Call → 参数校验 → 工具执行 → Observation → LLM → 最终回答。

当前不足：

Day 4 代码曾借助 AI 工具生成，虽然基本理解，但还不能完全独立手写。后续需要通过局部重写和原理讲解巩固，不需要推倒整个项目重做。

### Day 5：LLM Tool Calling

<已通过验收>

学习内容：
- Tool Schema 的作用。
- LLM 如何选择工具。
- Tool Calling 的执行流程。
- 参数解析与校验。
- FakeLLM 模拟。
- Observation 返回。
- 工具执行和业务校验的边界。

验收记录：
- 8 个测试通过。
- 阶段评分：90/100。

### Day 6：Multi-step Tool Calling / Agent Reliability

已在项目中实现并验证相关能力。

涉及：
- 多工具调用。
- 多步骤执行。
- 工具调用次数控制。
- 工具异常处理。
- 工具执行失败后的处理。
- 异常终止。
- Trace 记录。

注意：后续不能把已经实现的 Tool Calling 或 Reliability 内容重新包装成全新的学习任务。

### Day 7：Agent Execution Loop

<已通过验收>

重点学习：
- Agent Execution Loop。
- 多轮 LLM 调用。
- Context / Messages 传递。
- Tool Call → Observation → Final Answer。
- Agent State。
- Trace。
- 最大执行轮数与工具调用次数的区别。

主要测试结果：

`test_agent_loop.py`
- TC01：正常多轮执行。
- TC02：不需要工具时直接返回答案。
- TC03：后续 LLM 能获取前序工具 Observation。

结果：3 passed。

`test_agent_reliability.py`
- TC01：无参数工具和参数校验。
- TC02：工具只执行一次。
- TC03：订单工具异常。
- TC04：退款工具异常及 Trace。
- TC05：多工具调用时的最大次数限制。

结果：5 passed。

Day 7 总计：8 个相关测试通过。

目前已经能够理解并验证：
- Agent 多轮执行过程。
- 上一轮 Observation 如何进入下一轮 Context。
- `max_steps` 控制 Agent 执行轮数。
- `max_tool_calls` 控制累计工具调用次数。
- 工具异常和权限拒绝的处理。
- Trace 对执行过程的记录。

## 五、当前能力评估

### 已具备的能力

1. 理解 LLM 与 Agent 的基本区别。
2. 理解 Prompt 的基本结构和测试方向。
3. 理解 Tool Schema 与实际 Python Tool 的关系。
4. 理解 Tool Calling 的执行机制。
5. 能够使用 FakeLLM 模拟 LLM 响应。
6. 能够编写 Pytest 测试验证 Agent 执行链路。
7. 理解多轮执行和 Observation 传递。
8. 能够测试工具异常、权限拒绝和执行限制。
9. 能够阅读和修改现有 Agent 代码。

### 需要加强的能力

1. 独立手写 Agent 核心代码的能力。
2. 对 Agent 内部执行机制的深入理解。
3. Planning 与 Decision 的机制和边界。
4. 更复杂的 State / Context 管理。
5. Agent 执行过程的调试和问题定位。
6. 面试中对技术原理的准确表达。

### 当前学习原则

不追求代码量，也不追求测试用例数量。

重点是能够回答：
- Agent 为什么这样执行？
- LLM 如何决定调用哪个工具？
- Agent 如何控制执行流程？
- Observation 如何影响下一步决策？
- 出现异常时，Agent 应如何处理？
- 如何定位 Agent 执行失败的原因？

## 六、课程调整原则

后续课程必须先检查 GitHub 项目当前实现，再决定学习内容。

尤其注意：
- Tool Calling 已在 Day 5 学习。
- Multi-step Tool Calling 和 Reliability 的相关能力已在 Day 6 实现。
- Day 7 已验证 Execution Loop 和多轮 Context。
- 不应重复实现已经具备的功能。
- 如果某个知识点已经实现但理解不够，可以安排原理讲解、代码分析或针对性练习。
- 只有真正缺少的新技术能力，才安排新的编码任务。

Day 8 原计划为 Planning 与 Decision，但需要先检查当前项目是否已经覆盖相关能力，避免重复。

## 七、下一阶段学习方向

优先检查以下能力：

1. Planning：Agent 如何将用户目标拆分为多个步骤。
2. Decision：Agent 如何根据订单状态、工具结果和业务规则选择下一步。
3. Conditional Execution：不同条件下如何选择不同执行路径。
4. State：执行过程中的状态如何保存和更新。
5. Trace：如何根据执行轨迹定位决策错误。

建议使用同一个电商退款场景：

用户提出：
“查询订单 ORD1001，如果已经支付并且符合退款条件，就帮我退款。”

分析流程：
- 查询订单。
- 判断支付状态。
- 检查退款资格。
- 检查权限。
- 决定是否执行退款。
- 执行退款或拒绝。
- 返回最终结果。

学习重点是理解 Agent 的 Planning 和 Decision，而不是重新编写已有的 Tool Calling 或 Reliability 框架。

## 八、后续教学要求

每个新阶段遵循以下流程：

1. 先解释技术原理。
2. 结合当前项目分析已有代码。
3. 明确哪些能力已经实现、哪些只是表面实现、哪些尚未掌握。
4. 只安排必要的新代码练习。
5. 使用少量高价值测试验证。
6. 提交代码和测试结果。
7. 进行严格 Code Review。
8. 达到验收标准后进入下一阶段。

**最终目标：不仅能够编写 Agent 测试用例，还要真正理解 Agent 的运行机制，能够独立实现、测试、调试和分析 Agent。**