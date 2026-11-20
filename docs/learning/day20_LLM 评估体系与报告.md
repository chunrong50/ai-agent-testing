# **Day 20：LLM Evaluation 评估体系与测试报告**

第二阶段

Day 20 / 40

理论 + 实践

今天进入 LLM Evaluation 的最后一个核心主题：**如何把零散的评估指标和测试结果，组织成一套完整、可执行、可追踪的评估体系。**

Day 18 学习了评估指标、Evaluation Dataset 和 LLM-as-a-Judge。

Day 19 学习了可靠性与一致性测试。

今天不再重复这些基础知识，而是把它们组合起来，解决一个更接近真实工作的问题：

> 如果你负责测试一个电商退款 Agent，如何证明这个 Agent 达到了上线要求？如何向开发、测试负责人汇报评估结果？

## **一、今天的学习目标**

今天只掌握四个核心知识点：

| 知识点                    | 需要掌握的能力          |
| ---------------------- | ---------------- |
| 1. Evaluation Pipeline | 理解完整评估流程         |
| 2. Evaluation Strategy | 知道不同指标如何组合       |
| 3. Evaluation Report   | 能够设计评估报告         |
| 4. Release Criteria    | 能够根据评估结果判断是否可以上线 |

最终要求：能够独立设计一份 Agent 评估方案，并根据测试数据判断 Agent 是否满足上线条件。

## **二、知识点 1：完整的 LLM Evaluation 评估体系**

在真实项目中，不能只写几个测试用例，然后根据 pytest 的 Pass / Fail 判断 Agent 是否合格。

需要建立完整的 Evaluation Pipeline。

## **LLM Evaluation Pipeline**

**1. Evaluation Dataset**

准备评估数据集：正常请求、异常请求、业务规则、历史场景

**2. Agent Execution**

执行 Agent，收集响应、工具调用、执行记录

**3. Evaluation**

Correctness / Relevance / Faithfulness / Safety / Reliability / Consistency

**4. Result Aggregation**

统计通过率、失败率、各项指标得分、失败原因

**5. Evaluation Report**

生成评估报告，分析风险与质量问题

**6. Release Decision**

Pass / Fail / Conditional Release

这里有一个重要概念：

**Evaluation 不等于测试执行。**

测试执行负责产生数据，Evaluation 负责判断质量，Report 负责呈现结果，Release Criteria 负责决定是否上线。

这几个环节需要区分。

## **三、知识点 2：如何设计评估策略？**

假设现在有一个电商退款 Agent。

我们准备了 100 条 Evaluation Dataset，执行评估后得到以下结果。

以下是教学示例数据，不代表真实系统测试结果。

| 评估维度         | 结果   | 目标    |
| ------------ | ---- | ----- |
| Correctness  | 96%  | ≥ 95% |
| Relevance    | 98%  | ≥ 95% |
| Faithfulness | 92%  | ≥ 95% |
| Safety       | 100% | 100%  |
| Reliability  | 96%  | ≥ 95% |
| Consistency  | 94%  | ≥ 95% |

这里需要注意三个问题。

**问题 1：是否可以把所有指标取平均值，判断 Agent 是否合格？**

不可以简单这么做。

例如：

- Correctness：96%
- Relevance：98%
- Faithfulness：92%
- Safety：100%

即使平均分达到较高水平，也不能因为其他指标优秀，就忽略 Faithfulness 不达标的问题。

特别是 Safety，不能通过其他指标的高分进行抵消。

**问题 2：不同指标是否应该有不同的通过标准？**

应该。

例如：

- Safety：必须达到 100%。
- Correctness：至少达到 95%。
- Reliability：至少达到 95%。
- Consistency：至少达到 95%。

具体阈值由项目风险、业务要求和上线标准确定，并不是行业统一规定。

**问题 3：如果某个指标不达标怎么办？**

不能只报告一个 Fail。

还需要进一步分析：

1. 哪些测试用例失败？
2. 失败集中在哪些业务场景？
3. 是 Prompt 问题、LLM 输出问题，还是工具执行问题？
4. 是否会造成实际业务损失？
5. 修复之后是否需要重新评估？

这才是完整的评估思路。

## **四、知识点 3：如何设计 Evaluation Report？**

这部分是今天的重点。

假设你完成了一次退款 Agent 的评估，需要向测试负责人提交报告。

一份合格的报告至少需要以下内容。

### **1. 基础信息**

- Agent 版本
- Prompt 版本
- 测试时间
- Evaluation Dataset 版本
- 测试数据量

为什么需要记录这些信息？

因为 Agent 的评估结果可能受到模型版本、Prompt 版本和数据集变化的影响。

如果下次评估结果发生变化，需要能够追溯。

### **2. 评估指标统计**

例如：

## **Refund Agent Evaluation Report**

示例评估结果 · 100 条数据

未通过

# **96%**

Correctness

**Correctness**

96% / 95%

**Relevance**

98% / 95%

**Faithfulness**

92% / 95%

**Safety**

100% / 100%

**Reliability**

96% / 95%

**Consistency**

94% / 95%

**评估结论**

Faithfulness 和 Consistency 未达到预设标准，当前不满足全部上线条件。

### **3. 失败问题分析**

报告不能只写失败数量，还要分析失败原因。

例如：

| 问题           | 发现             | 风险 |
| ------------ | -------------- | -- |
| Faithfulness | Agent 编造订单退款状态 | 高  |
| Consistency  | 相同输入产生不同判断     | 中  |
| Safety       | 暂无失败           | —  |

这里的风险等级应当结合实际业务影响判断。

### **4. 最终评估结论**

需要明确回答：

- Agent 是否满足上线标准？
- 哪些指标不合格？
- 是否存在高风险问题？
- 是否需要修复后重新测试？

**测试报告的价值不是展示测试执行了多少条，而是帮助团队判断产品质量和上线风险。**

## **五、知识点 4：Release Criteria（上线准入标准）**

这是评估体系最后一个环节。

假设项目规定：

| 指标           | 上线标准  |
| ------------ | ----- |
| Correctness  | ≥ 95% |
| Relevance    | ≥ 95% |
| Faithfulness | ≥ 95% |
| Safety       | 100%  |
| Reliability  | ≥ 95% |
| Consistency  | ≥ 95% |

那么刚才的评估结果应该如何判断？

答案是：**不通过上线验收。**

原因：

- Faithfulness = 92%，低于 95%。
- Consistency = 94%，低于 95%。

即使其他指标都通过，也不能判定整体合格。

实际项目中还需要考虑：

- 是否存在严重业务错误？
- 是否存在未解决的安全问题？
- 是否有已知问题被正式接受？
- 修复之后是否完成回归评估？

这里要建立一个测试工程师的重要思维：

> 上线判断应该基于预先定义的质量门槛和风险，而不是根据整体平均分或者主观感觉。

# **六、Day 20 实践任务**

今天不要求你重新开发 Agent，也不要求增加大量测试用例。

我们直接使用已有的电商退款 Agent 评估场景，练习设计评估报告。

## **练习 20-01：分析评估结果**

假设本次评估数据如下：

| 指标           | 实际结果 | 上线要求  |
| ------------ | ---- | ----- |
| Correctness  | 97%  | ≥ 95% |
| Relevance    | 96%  | ≥ 95% |
| Faithfulness | 93%  | ≥ 95% |
| Safety       | 100% | 100%  |
| Reliability  | 92%  | ≥ 95% |
| Consistency  | 98%  | ≥ 95% |

请回答：

1. 本次 Agent 是否通过评估？
2. 哪些指标不满足要求？
3. 能否使用所有指标的平均分判断 Agent 是否通过？
4. 如果 Reliability 不合格，你会优先调查哪些方面？
5. 如果 Safety 出现一次未经授权的退款执行，即使其他指标全部合格，是否允许上线？为什么？

## **练习 20-02：设计一份评估报告**

请你按照下面的结构，写一份简化版报告。

# Refund Agent Evaluation Report

## 1. 测试基本信息

- Agent 版本： 
- Prompt 版本：
- Dataset 数量：
- 测试时间：

## 2. 评估结果

- Correctness：
- Relevance：
- Faithfulness：
- Safety：
- Reliability：
- Consistency：

## 3. 问题分析

- 未通过的指标：
- 失败原因：
- 潜在业务风险：

## 4. 最终评估结论

- 是否满足上线标准：
- 是否需要修复：
- 是否需要重新评估：

## 5. 测试建议

- 优先修复的问题：
- 后续需要关注的指标：

## **七、Day 20 验收标准**

今天不追求写很多代码，重点考察你能否从测试执行者转变为评估体系设计者。

| 验收项目          | 标准            |
| ------------- | ------------- |
| Pipeline      | 能解释完整评估流程     |
| Metrics       | 能区分各项指标的作用    |
| Report        | 能独立编写评估报告     |
| Release       | 能根据准入标准判断是否上线 |
| Risk Analysis | 能识别高风险评估失败    |

**通过要求：** 能够独立完成 20-01 和 20-02，并解释自己的判断依据。

### **今天特别强调**

Day 18、19、20 三天实际上构成了一条完整的知识链：

- Day 18：如何评估 LLM 的回答质量？
- Day 19：如何评估 LLM 的可靠性和一致性？
- Day 20：如何将评估结果形成体系，并判断是否达到上线要求？

这三个主题学完后，LLM Evaluation 的第一轮学习就完成了。

**先完成 20-01 的五道题，我会逐题评审你的判断，再验收评估报告。**