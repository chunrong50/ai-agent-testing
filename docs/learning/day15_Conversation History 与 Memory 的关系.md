# **Day 15：AI Agent 测试实战进阶**

今天开始 Day 15。

从 Day 13、Day 14 的学习内容来看，我们已经从简单的 Agent 执行机制，逐步进入 **LLM Plan Agent 的执行控制、异常恢复和业务一致性测试**。

Day 15 不再重复学习基础 Tool Calling 或 Plan 生成，而是进一步学习如何测试一个 Agent 在复杂执行过程中是否能够正确处理状态、异常和决策。

今天仍然遵循我们的学习原则：

- 以达到 AI Agent 测试工程师面试要求为目标。
- 少而精，优先掌握高价值知识点。
- 结合现有 `ai-agent-testing` 项目学习，不重新搭建框架。
- 先理解原理，再做小规模代码练习。
- 我负责逐项评审，达到验收标准后再进入下一天。

## **一、Day 15 学习主题**

Day 15

**Plan Failure Recovery & Replanning**

Plan 执行失败后的恢复与重新规划

今天重点解决一个问题：

**当 Agent 执行 Plan 的某个 Step 失败时，什么时候应该重试，什么时候应该重新规划，什么时候应该直接终止？**

### **1. 为什么需要学习这个知识点？**

回顾目前的 `LLMPlanAgent`：

假设 LLM 生成了一个退款 Plan：

1. **Step 1：query_order**

   查询订单 A10086

   completed
2. **Step 2：check_permission**

   检查用户是否有订单操作权限

   completed
3. **Step 3：execute_refund**

   执行退款

   failed

现在问题来了：Step 3 失败后，Agent 应该怎么办？

可能存在三种处理方式：

| 处理方式      | 适用情况    | 示例                |
| --------- | ------- | ----------------- |
| Retry     | 临时性故障   | 网络超时、服务暂时不可用      |
| Replan    | 原计划不再适用 | 订单状态发生变化，需要调整后续步骤 |
| Terminate | 无法继续执行  | 用户无权限、订单不满足退款条件   |

这三种处理方式是今天的核心。

### **2. 必须理解的三个概念**

**① Retry：重试当前 Step**

原有 Plan 不变，只重新执行失败的 Step。

例如：

- 查询订单时发生网络超时。
- 后端服务返回临时错误。
- 满足重试条件，且操作具有安全的重试机制。

注意：退款操作不能因为超时就盲目重试。必须先查询退款结果，防止重复退款。

**② Replan：重新生成 Plan**

原来的 Plan 已经不适用，需要根据最新 Observation 重新规划。

例如：

原 Plan：

```
Step 1: query_order
Step 2: check_permission
Step 3: execute_refund
```

执行 Step 1 后发现订单已经退款。

原来的退款计划不再适用，Agent 应根据最新订单状态重新规划，或者直接结束任务。

**③ Terminate：终止执行**

例如：

- 权限校验失败。
- 订单不属于当前用户。
- 订单不符合退款业务规则。
- 达到最大重试次数。

这些情况不能通过不断重试来解决。

### **3. Agent 测试应该关注什么？**

今天不追求大量 Test Cases，重点关注以下四个测试能力：

| 测试能力              | 核心验证                        |
| ----------------- | --------------------------- |
| Retry             | 是否只重试允许重试的 Step             |
| Replan            | 是否根据最新 Observation 生成新 Plan |
| State Consistency | 旧 Step 状态是否正确保留或更新          |
| Safety            | 是否避免重复退款、越权执行               |

尤其注意一个重要原则：

**Replan 不等于重新执行全部步骤。**

例如，订单查询和权限检查已经成功，不应该因为退款 Step 失败就无条件重新执行全部操作。

这也是我们后续代码评审的重点。

## **二、Day 15-01：知识理解检查**

今天先不写代码。先确认你能否区分 Retry、Replan 和 Terminate。

下面三个场景，请逐一判断。

**Day 15-01 知识检查**

3/3 已回答

**场景 1：query_order 执行时发生网络超时。系统确认没有产生任何业务副作用，且该工具允许安全重试。Agent 应该怎么处理？**

Retry 当前 Step

Replan 整个 Plan

Terminate 整个 Plan

正确

参考答案：Retry 当前 Step

这是临时性故障，原 Plan 仍然有效，可以安全重试当前 Step。

**场景 2：query_order 成功，返回订单状态已经 REFUNDED，但原 Plan 仍然包含 execute_refund。Agent 应该怎么处理？**

Retry execute_refund

Replan 或终止当前任务

忽略订单状态，继续执行

正确

参考答案：Replan 或终止当前任务

原计划已经不符合最新业务状态，不能继续执行退款。

**场景 3：check_permission 返回 PERMISSION_DENIED。Agent 应该怎么处理？**

Retry 当前 Step

Replan 并尝试其他退款工具绕过权限

Terminate 整个 Plan

正确

参考答案：Terminate 整个 Plan

权限拒绝是明确的业务阻断条件，不能通过重试或更换工具绕过。

提交答案重新作答

# **3/3**

完成后，把你的判断理由也发给我。

## **三、今天的学习安排**

| 阶段        | 内容                         | 要求              |
| --------- | -------------------------- | --------------- |
| Day 15-01 | Retry / Replan / Terminate | 理解并区分           |
| Day 15-02 | Replanning 执行机制            | 理解 Plan 更新和状态管理 |
| Day 15-03 | Pytest 自动化测试               | 编写核心测试          |
| Day 15-04 | 代码评审与面试总结                  | 达到验收标准          |

今天先完成 Day 15-01，不急着写代码。

**你先完成上面的三个问题，并说明每个场景为什么选择这种处理方式。** 我会按照面试标准评审你的答案，然后带你进入现有 `LLMPlanAgent` 的代码实现。