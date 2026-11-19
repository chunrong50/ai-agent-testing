今天进入 **Day 19：LLM Evaluation——评估可靠性与一致性测试**。

Day 18 我们已经建立了 LLM Evaluation 的基本框架：

- Evaluation Dataset：评估数据集
- Evaluation Metrics：评估指标
- `evaluate_response()`：规则化评估
- `evaluate_with_judge()`：使用 LLM-as-a-Judge 进行评估

Day 19 不再重复这些基础内容，而是进一步解决一个实际问题：

**同样的输入，LLM 每次给出的结果不一样，我们如何判断 Agent 是否可靠？**

# **Day 19 学习目标**

**本日核心主题**

面试重点

# **LLM Reliability & Consistency**

理解 LLM 输出的不确定性，并建立可重复执行的评估机制。

**今天只掌握三个知识点**

1. **Reliability（可靠性）**

   多次运行后，Agent 是否能够持续满足业务要求？
2. **Consistency（一致性）**

   相同输入多次执行，结果是否保持稳定？
3. **Repeated Evaluation（重复评估）**

   如何通过多次执行、统计结果，量化 Agent 的可靠程度？

# **一、为什么需要可靠性与一致性测试？**

先看一个电商退款 Agent 的例子。

用户输入：

> 帮我查询订单 ORD1001 是否可以退款。

业务系统返回：

```
{    "order_id": "ORD1001",    "status": "paid",    "refund_status": "not_refunded"}
```

业务规则：订单已支付且未退款，符合退款条件。

现在让 Agent 对相同输入执行 5 次：

| 执行次数  | Agent 输出 | 评估结果 |
| ----- | -------- | ---- |
| 第 1 次 | 可以退款     | Pass |
| 第 2 次 | 可以退款     | Pass |
| 第 3 次 | 不能退款     | Fail |
| 第 4 次 | 可以退款     | Pass |
| 第 5 次 | 可以退款     | Pass |

这里出现了一个问题：

Agent 第三次为什么改变了判断？

可能原因：

- LLM 本身存在随机性。
- Prompt 对结果的约束不够明确。
- Context 在不同执行过程中存在差异。
- LLM 对业务规则的理解不稳定。

这就是我们需要进行可靠性与一致性测试的原因。

# **二、两个核心指标**

**1. Reliability：可靠性**

关注的是：多次执行中，有多少次满足预期业务要求。

例如：

\\[ Reliability = \frac{Pass次数}{总执行次数} \\]

上面的案例：

\\[ Reliability = \frac{4}{5}=80\\% \\]

意味着 Agent 在这组测试中的业务通过率为 80%。

**2. Consistency：一致性**

关注的是：相同输入重复执行时，结果是否稳定。

例如：

```
第1次：可以退款
第2次：可以退款
第3次：不能退款
第4次：可以退款
第5次：可以退款
```

这里出现了两种不同的判断，因此结果不一致。

注意一个面试重点：

**可靠性和一致性不是同一个概念。**

例如，一个 Agent 每次都回答：

```
订单不能退款
```

它的输出非常一致，但如果订单实际上符合退款条件，那么它的可靠性仍然很差。

因此：

- 一致性关注结果是否稳定。
- 可靠性关注结果是否持续满足预期。

# **三、如何进行自动化测试？**

我们不需要重复写大量业务测试用例。

只需要增加一个重复执行评估机制。

假设已经有 Day 18 的 Evaluation Dataset：

```
test_case = {    "input": "查询订单ORD1001是否可以退款",    "expected": "可以退款"}
```

现在增加一个核心函数：

```
def evaluate_reliability(    agent,    test_case,    repeat=5):    results = []    for _ in range(repeat):        response = agent.run(test_case["input"])        result = evaluate_response(            response,            test_case["expected"]        )        results.append(result)    pass_count = sum(results)    return {        "total": repeat,        "passed": pass_count,        "reliability": pass_count / repeat    }
```

这里最重要的是理解：

原来的 Evaluation 是：

```
输入 → Agent → 评估 → 得到结果
```

现在变成：

```
                 ┌→ Agent → 评估 → Result 1
                 ├→ Agent → 评估 → Result 2
相同测试输入 ────┼→ Agent → 评估 → Result 3
                 ├→ Agent → 评估 → Result 4
                 └→ Agent → 评估 → Result 5
                              ↓
                         统计可靠性
```

这就是 Repeated Evaluation。

注意：这里的示例代码是教学简化版，实际测试还需要保证每次执行的用户输入、业务数据和测试环境一致，避免把环境变化误判成 LLM 随机性。

# **四、Day 19 知识检查**

今天先不写代码，先确认你是否真正理解了可靠性与一致性的区别。

**Day 19-01 知识验收**

0/3 已回答

**1. 同一个退款请求执行5次，5次全部返回“不能退款”，但实际上订单符合退款条件。应该如何评价？**

可靠性高，一致性高

可靠性低，一致性高

可靠性高，一致性低

可靠性低，一致性低

**2. 同一个测试输入执行10次，其中9次通过、1次失败。可靠性是多少？**

10%

80%

90%

100%

**3. 为什么不能只执行一次 Agent 测试，就判断 LLM 的输出可靠？**

因为 Agent 每次必须调用不同工具

因为 LLM 输出可能存在随机性，单次结果无法反映重复执行的稳定程度

因为 Pytest 不能执行 Agent

因为所有 LLM 输出都不可信

提交答案

# **五、今天的学习范围**

今天不要求你学习复杂的统计学，也不要求接入真实 LLM API。

先掌握：

1. 能区分 Reliability 和 Consistency。
2. 能解释为什么需要重复执行 Agent。
3. 能理解如何计算可靠性通过率。

通过知识验收后，我们再实现一个简化的 `evaluate_reliability()`，用 Pytest 验证重复执行与结果统计。

**今天的重点不是增加测试用例数量，而是让测试从单次正确性验证，升级为多次执行的质量评估。**

我会在后续课程中用同一套评估框架，继续带你理解如何区分 Agent 自身的不稳定与 Judge 评估器的不稳定。