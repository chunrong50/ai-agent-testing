我的建议是：**原来的&#x20;**`persistence.py`**&#x20;练习不再作为独立任务，调整为 Day 17 的一个小型实践环节。整体学习方向做一次修正。**

原因是我们刚才已经明确了 AgentState 和 Persistence 的关系。如果只是单独实现 JSON 的序列化、反序列化，学习价值有限，还容易偏离你当前的主要目标——掌握 Agent 测试和面试能力。

## **一、Day 17 新安排**

调整后的学习安排

**主题：Agent Checkpoint & Persistence（状态检查点与持久化恢复）**

| 学习内容           | 是否保留 | 学习重点       |
| -------------- | ---- | ---------- |
| AgentState     | 不重复  | 已掌握        |
| Plan / Step 状态 | 不重复  | 已掌握        |
| Persistence 原理 | 保留   | 理解为什么需要    |
| Checkpoint     | 新增   | 什么时候保存状态   |
| JSON 序列化       | 简化实践 | 理解状态保存和加载  |
| Resume         | 重点   | 如何恢复执行     |
| 幂等性            | 重点   | 如何避免重复执行退款 |

## **二、今天真正需要完成的任务**

我把任务压缩为三个部分：

**Day 17-01：Checkpoint 设计**

理解 Agent 在哪些关键节点保存状态，以及为什么不需要每一步都保存所有数据。

**Day 17-02：Persistence 简单实现**

不要求重新设计 Plan 和 Step，只需要实现：

```
save_checkpoint(state)load_checkpoint(checkpoint_id)
```

让现有 AgentState 可以保存和恢复。

**Day 17-03：Agent Resume**

把恢复机制接入现有 LLMPlanAgent，验证恢复后：

- 已完成的 Step 不重复执行。
- 未完成的 Step 根据状态和恢复策略处理。
- 已有 Observation 不丢失。
- 不重复执行已经成功产生业务结果的退款操作。

## **三、Day 17 的验收标准**

不再要求大量测试用例，重点看三个能力：

1. 能够解释 AgentState、Checkpoint、Persistence 三者的关系。
2. 能够设计 Agent 中断后的恢复机制。
3. 能够通过少量 Pytest 验证恢复执行的正确性。

## **四、后续学习计划也做相应调整**

我们不再为了完成 80 天而扩充内容，继续按照此前确定的第一阶段 20 天、第二阶段 20 天的精简方向推进。

**Day 17 完成后，不再单独安排一整天学习数据库、Redis 或 JSON 存储技术。** 这些属于实现手段，不是当前阶段的核心学习目标。

### **现在开始 Day 17-01**

我们先从一个实际问题入手：

假设你的退款 Agent 执行：

```
Step01：query_order       completed
Step02：check_permission  completed
Step03：execute_refund    completed
Step04：send_notification pending
```

此时 Agent 进程突然崩溃。

你需要设计一个 Checkpoint 保存机制，确保重启后能够从 Step04 继续，而不是重新执行退款。

**今天先设计这个机制，不再重复考查之前已经掌握的状态概念。**