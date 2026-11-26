AI Agent 测试学习档案（截至 2026-11-26）
Day 23 已完成
当前进度：Day 24

首先明确当前进度：你现在正在学习 Day 24，不是 Day 23。

后续所有课程衔接、代码评审、学习任务和进度记录，均以 Day 24 为当前起点。Day 23 已经结课，不再重复学习。
一、学习目标与路线
你的学习目标是：尽快达到 AI Agent 测试岗位的面试与实际项目能力。

目前采用的是你在 2026-11-20 明确指定的 40 天学习计划，这是唯一有效的学习路线。

学习原则：
1. 不为了凑满 40 天而增加低价值内容。
2. 不重复已经掌握的知识和测试细节。
3. 以 Agent 测试技术体系为主，而不是单纯堆积 Test Case。
4. 重点掌握架构、执行链路、测试方法、质量评估和自动化框架。
5. 采用导师式学习：知识讲解 → 实践 → 提交代码 → Pytest 结果 → 严格评审 → 验收。
二、个人技术基础
项目	当前情况
软件测试经验	10年以上
编程语言	Python
自动化框架	Pytest
业务经验	电商、支付
当前基础	功能测试、自动化测试、业务测试
学习项目	ai-agent-testing
学习环境	Python + Pytest

项目仓库：
ai-agent-testing（GitHub）主要目录：
- src/：Agent、Tools 等实现代码
- tests/：自动化测试代码
- tests/conftest.py：公共 Fixture 和测试对象初始化
- tests/week01/：前期 Agent 测试练习

三、40 天学习进度总览
以下是当前路线的进度定位。
阶段	学习内容	进度
Day 1–20	Agent 基础、执行链路、Tool Calling、Plan、Memory 等	已完成
Day 21–22	Pytest 测试框架、Fixture、FakeLLM、Mock、测试数据管理	已完成
Day 23	RAG 完整架构与基础测试	已完成
Day 24	RAG 深入测试	正在学习
Day 25–26	Memory 深入测试	待学习
Day 27–28	Workflow / Multi-Agent	待学习
Day 29–30	Agent 自动化测试框架	待学习
Day 31–32	DeepEval / LLM Judge	待学习
Day 33–34	LangSmith / Trace	待学习
Day 35–36	Agent 回归测试与 CI	待学习
Day 37–38	Agent 安全、性能与稳定性	待学习
Day 39–40	电商支付 Agent 综合项目	待学习

注意：Day 23–24 是两个不同的学习单元。Day 23 已验收，Day 24 正在进行。
四、Day 23 学习档案：RAG 完整架构与基础测试
已完成并验收
1. 学习内容
掌握了 RAG 的完整执行链路：
Query：用户问题


Embedding：问题向量化


Retrieval：知识库检索


Rerank：检索结果重新排序


Context：构建 LLM 上下文


LLM：结合上下文生成回答


Final Answer：最终答案


2. 已掌握的测试能力
测试方向	掌握情况
Retrieval Quality	检索准确性、相关性
Context Integrity	检索内容是否正确传递给 LLM
Answer Faithfulness	回答是否忠实于检索证据
RAG 执行链路	各阶段数据传递与验证
Pytest 实践	FakeRetriever、FakeLLM、Fixture

3. Day 23 最终实践结果
你已经完成 Day 23-03 的测试实践：
- Retrieval Quality：验证检索结果。
- Context Integrity：验证正确的文档进入 LLM 上下文。
- Answer Faithfulness：验证最终答案是否有证据支持。
最后一次评估结果：
项目	结果
Faithfulness	2/4
Faithfulness 得分	0.5
代码评审	88/100
Pytest	通过

涉及的代码对象：
- LLMPlanAgent
- agent_factory
- FakeRetriever
- FakeLLM
- AgentState.final_response
- Evaluator.faithfulness
Day 23 的结论：已经完成 RAG 基础架构理解和主要测试能力实践，不需要重新学习。

五、Day 24 学习档案：RAG 深入测试
当前正在进行
Day 24 的核心目标不是重新学习 RAG，而是深入验证 RAG 的检索质量和知识可靠性。

目前确定的三个重点：
1. Reranker 排序测试。
2. 知识库更新测试。
3. 证据不足时的幻觉分析与测试。
Day 24-01：Reranker 测试
当前正在进行代码评审
目前你正在实现：

test_01_reranker()

涉及的测试组件：
- FakeRetriever
- FakeReranker
- documents
- Retriever 返回的初始文档列表
- Reranker 返回的重新排序结果
当前测试问题：

用户问题：

已支付订单如何申请退款

初始检索结果：

D001、D002、D003、D004、D005

你希望通过 Reranker 将更相关的文档排在前面，重点关注：
- D003
- D005
当前测试重点是验证：
1. Reranker 是否正确执行重新排序。
2. 相关文档是否被排在前面。
3. 排序后是否出现文档丢失。
4. 排序后是否出现重复文档。
5. 最终结果是否符合预期排序。
当前学习位置：Day 24-01，Reranker 测试代码评审与完善。

接下来应当继续你当前的 test_01_reranker()，而不是跳回 Day 23，也不是直接跳到 Day 24 后续内容。

六、后续学习安排
从当前 Day 24 继续，按照以下顺序推进：
顺序	学习主题	核心能力
Day 24-01	Reranker 测试	排序质量、相关性、结果完整性
Day 24-02	知识库更新测试	文档新增、修改、删除后的检索一致性
Day 24-03	RAG 幻觉测试	证据不足、无相关文档、无依据回答
Day 24 验收	综合 RAG 测试	从检索到最终回答的质量验证

完成标准：能够独立设计测试方案、编写 Pytest 测试代码，并解释测试背后的质量风险。
七、后续代码评审要求
继续保持之前约定的评审方式：
- 重点检查测试思路是否正确，而不是单纯检查语法。
- 评价测试是否验证了真实的 Agent/RAG 行为。
- 指出不合理的断言、测试数据设计和 Mock 使用。
- 避免为了覆盖率设计大量重复的异常 Case。
- 优先选择少而精、有业务价值的测试。
- 对不理解的代码提供简化实现，让你能够独立编写。
每次代码评审给出分数、问题分析、修改建议和验收结论。
八、当前学习档案的正式记录
当前学习状态
正式学习进度
Day 24


Day 23
完成

Day 24
进行中

当前任务
Day 24-01 Reranker

当前阶段
RAG 深入测试

学习路线
40 天计划（唯一有效路线）


下一步：继续评审 Reranker 测试代码。

进度管理规则：
1. Day 23 永久标记为已完成，不再作为当前学习日。
2. 当前学习日固定为 Day 24。
3. 只有 Day 24 完成验收后，才进入 Day 25。
4. 不擅自调整 40 天路线，不重复已经通过的学习内容。
5. 后续生成学习档案时，必须以最新验收进度为准。
接下来我们直接从 Day 24-01：Reranker 测试代码评审 继续。