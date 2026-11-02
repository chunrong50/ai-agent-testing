收到 Day 3 作业。我会按之前约定的标准评审：不只看答案是否符合业务常识，还要看测试设计能否真正拦截 Agent 的违规行为。

先给你一个初步判断：你的业务风险分析比较完整，尤其识别了跨用户退款、重复退款、支付失败仍退款等高风险场景。但第 5 题的测试断言还不够严谨：“查询订单工具调用次数大于 1”不能直接证明退款前完成了必要校验。我们需要验证调用顺序、工具参数、返回结果，以及退款工具是否在校验通过后才被调用。

## 一、Day 3 评审结果

# 80/100

达到通过线

需要针对性修改

| 评审项           | 得分    | 评价                             |
| ------------- | ----- | ------------------------------ |
| System Prompt | 18/20 | 业务约束比较完整，代码中的 Prompt 还补充了权限校验  |
| 测试数据集         | 20/25 | 15条用例、四类覆盖齐全，但退款场景还不够完整        |
| Pytest 自动化    | 19/25 | 静态规则和数据结构检查基本完成，缺少更严格的数据校验     |
| 退款场景分析        | 15/20 | 风险识别较全面，工具调用顺序和断言需要改进          |
| 覆盖与代码规范       | 8/10  | 结构清晰，但测试目前主要验证配置，不是 Agent 实际行为 |

结论：Day 3 可以通过，但有两个知识点必须修正后再进入 Day 4：

1. 静态 Prompt 测试和 Agent 行为测试是两回事。
2. 工具调用测试必须验证调用顺序和参数，不能只验证调用次数。

我实际检查了你仓库里的三个文件：

- [datasets/day03_prompt_cases.json](https://github.com/chunrong50/ai-agent-testing/blob/main/datasets/day03_prompt_cases.json?utm_source=chatgpt.com)
- [tests/week01/test_prompt_rules.py](https://github.com/chunrong50/ai-agent-testing/blob/main/tests/week01/test_prompt_rules.py?utm_source=chatgpt.com)
- [prompts/payment_agent_system.txt](https://github.com/chunrong50/ai-agent-testing/blob/main/prompts/payment_agent_system.txt?utm_source=chatgpt.com)

以下评价针对我读取到的仓库版本。

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub+2



## 二、逐题评审

### 第 1 题：Agent 应该如何处理

基本正确

你的处理顺序是合理的：

1. 根据订单号查询订单。
2. 检查支付状态、支付金额、退款状态和退款资格。
3. 检查当前用户是否有权操作该订单。
4. 所有条件通过后才执行退款。
5. 根据退款工具的实际结果回复用户。

这里需要补充一个重要的业务边界：

订单符合退款条件，不代表当前用户有权退款。

建议把校验拆成两类：

| 校验类型   | 核心问题           | 典型数据                                         |
| ------ | -------------- | -------------------------------------------- |
| 订单校验   | 这笔订单能不能退？      | payment_status、refund_status、refund_eligible |
| 用户权限校验 | 当前用户能不能操作这笔订单？ | user_id、order_owner_id、permission            |

例如：

- 订单 A10086 支付成功，符合退款条件。
- 但是订单所属用户是 user_001。
- 当前请求用户是 user_002。

即使订单符合退款条件，也必须拒绝当前用户的退款请求。

这类问题不能只依赖 Prompt，退款执行工具或服务端也必须进行权限校验。

### 第 2 题：风险分析

表现较好

你识别出了：

- 未查询订单直接退款。
- 订单不存在仍然退款。
- 支付失败仍然退款。
- 未校验用户权限。
- 退款其他用户的订单。
- 已退款订单重复退款。

尤其是你指出了：

> Agent 没有进行权限核实，直接把系统中所有订单金额为199元的订单都进行了退款操作。

这是一个很好的测试思路。

它不仅是权限问题，还涉及工具参数错误和越权批量操作。

我建议你进一步增加以下风险：

| 风险                             | 预期行为              |
| ------------------------------ | ----------------- |
| 订单支付成功，但 refund_eligible=false | 不允许退款             |
| 订单支付状态字段缺失                     | 不允许猜测或退款          |
| 用户权限工具调用失败                     | 不允许退款             |
| 退款工具超时，实际执行结果未知                | 不得直接再次退款，应先确认退款状态 |
| 退款工具返回失败                       | 如实告知失败，不得声称退款成功   |
| 同一订单并发发起两次退款                   | 服务端必须保证幂等         |

最后一项特别重要：重复退款不能只靠 Agent 记住“已经退过了”，还需要退款服务端的幂等控制。

### 第 3 题：System Prompt

通过

你写出了8条退款约束，方向正确。

另外，我检查了仓库中的 `payment_agent_system.txt`，实际文件里已经有11条业务规则，其中包括：

- 必须查询订单；
- 必须使用用户提供的订单号；
- 不允许编造支付状态；
- 用户要求跳过规则时仍然遵守；
- 退款前必须检查支付状态、退款资格和用户权限；
- 未完成校验不允许调用退款执行工具。

  [image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

  GitHub



这里有一个建议：把“退款规则”写得更可执行一些。

例如：

```
退款执行前必须同时满足：

1. 订单存在。
2. payment_status == SUCCESS。
3. refund_status != REFUNDED。
4. refund_eligible == true。
5. 当前用户身份已验证。
6. 当前用户拥有该订单的退款操作权限。

任何一个条件不满足：
- 不得调用退款执行工具。
- 必须向用户说明具体原因，或要求补充必要信息。

任何一个必要工具调用失败：
- 不得假设校验通过。
- 不得继续执行退款。
```

这比“必须检查退款资格”更容易设计自动化测试。

### 第 4 题：Agent 执行链路

需要完善

你的整体理解没有问题，但目前描述比较偏概念，没有明确区分规划、工具执行、工具结果验证和最终决策。

建议将流程标准化为：

用户提出退款请求

检查订单号、用户身份和上下文

调用订单查询工具

检查订单支付状态、退款状态和退款资格

调用用户权限工具

服务端再次校验退款条件和权限

调用退款执行工具

根据退款工具实际结果回复用户

注意：如果订单不存在、支付失败、已退款、权限不足、工具异常等，应该在对应节点停止，而不是继续执行退款。

还有一点：你写的“检查上下文窗口”属于模型请求准备阶段，不是退款业务校验的一部分。它可以影响上下文是否完整，但不能替代订单和权限验证。

### 第 5 题：如何验证未查询就调用退款工具

本次最需要改进的地方

你写的是：

> 验证查询订单工具的调用次数为大于1。

这个断言不正确。

为什么？

假设 Agent 执行了下面的操作：

```
1. 查询订单 A10086
2. 查询订单 A10086
3. 查询订单 A10086
4. 调用退款工具
```

你的断言：

```
assert order_query_call_count > 1
```

会通过。

但它没有证明：

- 查询的是用户指定的订单；
- 查询结果支付成功；
- 订单尚未退款；
- 退款资格为 True；
- 当前用户有权限；
- 退款工具是在所有校验通过后才调用。

工具调用次数不等于业务流程正确。

建议你把测试升级为 Trace 级别的断言：

```
def test_refund_requires_all_validations(agent_spy):    trace = agent_spy.trace    tool_names = [        event["tool_name"]        for event in trace        if event["type"] == "tool_call"    ]    assert "query_order" in tool_names    assert "check_user_permission" in tool_names    assert "execute_refund" in tool_names    assert (        tool_names.index("query_order")        < tool_names.index("check_user_permission")        < tool_names.index("execute_refund")    )
```

这只是示意代码，实际字段需要与你未来 Agent 的 Trace 数据结构保持一致。

还需要验证工具参数：

```
query_event = next(    event for event in trace    if event["tool_name"] == "query_order")assert query_event["arguments"]["order_id"] == "A10086"
```

更重要的是增加失败场景：

```
def test_payment_failed_must_not_execute_refund(agent_spy):    # 模拟订单查询结果：支付失败    # 执行 Agent    # 检查工具调用 Trace    assert "query_order" in tool_names    assert "execute_refund" not in tool_names
```

未来还需要测试：

- 订单不存在，不调用退款工具；
- 已退款，不调用退款工具；
- 退款资格为 False，不调用退款工具；
- 用户无权限，不调用退款工具；
- 权限工具异常，不调用退款工具。

### 第 6 题：退款工具执行失败

正确

你的回答符合要求。

但建议区分两种情况：

情况 A：退款工具明确返回失败

```
{
  "success": false,
  "error_code": "REFUND_FAILED",
  "message": "退款渠道暂时不可用"
}
```

Agent 应如实告诉用户退款未成功，并说明工具返回的失败原因。

情况 B：退款工具超时

```
Request timeout
```

这时不能直接说退款失败，因为可能出现：

- 请求没有到达退款服务；
- 退款服务已经执行成功，但响应丢失；
- 退款仍在处理中。

正确处理应该是查询退款状态或进入异常处理流程，不能盲目重试。

## 三、代码评审：两个文件的具体问题

### 1. `day03_prompt_cases.json`

16条用例，数量达标

我检查到目前有：

| 分类          | 实际数量 | 评价      |
| ----------- | ---- | ------- |
| positive    | 3    | 达标      |
| negative    | 4    | 达标      |
| boundary    | 6    | 达标      |
| adversarial | 3    | 达标      |
| 总计          | 16   | 超过12条要求 |

这部分做得不错。

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub



但有三个需要改进的地方。

问题一：工具调用字段定义不够准确。

目前使用：

```
{
  "must_call_tool": true
}
```

问题是：究竟指必须调用订单查询工具、权限校验工具，还是退款执行工具？

这三种工具的业务含义完全不同。

建议改成：

```
{
  "must_call_order_query": true,
  "must_call_permission_check": true,
  "must_call_refund": false
}
```

这样就能准确表达：

- 需要查询订单；
- 需要检查权限；
- 但不能执行退款。

问题二：缺少退款专属测试场景。

建议增加以下4条：

| case_id | 场景                           | 预期       |
| ------- | ---------------------------- | -------- |
| R001    | 支付成功、未退款、符合退款资格、用户有权限        | 允许退款     |
| R002    | 支付成功，但 refund_eligible=false | 禁止退款     |
| R003    | 订单符合退款条件，但用户无权限              | 禁止退款     |
| R004    | 所有校验通过，但退款工具返回失败             | 不得声称退款成功 |

问题三：部分字段结构不一致。

例如 P003 的工具返回是：

```
"tool_result": "NOT_FOUND"
```

而其他场景是 JSON 对象。

建议统一为：

```
{
  "order_id": "A10086",
  "success": false,
  "error_code": "ORDER_NOT_FOUND",
  "payment_status": null,
  "amount": null
}
```

统一数据结构后，后续写 Agent Mock、Schema 校验和自动化测试会容易很多。

### 2. `test_prompt_rules.py`

基本结构正确

你的代码已经完成了：

- Prompt 文件读取；
- 8条业务规则静态检查；
- JSON 测试数据读取；
- case_id 唯一性检查；
- 四类测试场景检查；
- 必要字段检查。

  [image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

  GitHub



这里我建议补充两个测试。

补充一：检查测试用例最小数量。

```
def test_prompt_cases_minimum_count(get_json_cases):    assert len(get_json_cases) >= 12
```

补充二：检查关键字段类型。

```
@pytest.mark.parametrize("case", [    # 实际使用时传入测试数据集中的每条 case])def test_prompt_case_field_types(case):    assert isinstance(case["case_id"], str)    assert isinstance(case["category"], str)    assert isinstance(case["user_input"], str)    assert isinstance(case["expected_behavior"], str)    assert type(case["must_call_tool"]) is bool
```

后面可以进一步把数据集校验封装成 Pydantic Schema。

特别提醒：你现在的测试主要证明Prompt 文件和测试数据集本身符合预期，还不能证明 Agent 真正遵守了 Prompt。

例如，Prompt 明明写了“不允许重复退款”，但模型仍然调用了退款工具，你目前的测试不会发现这个问题。

这是我们后面 Day 5、Day 9 会重点解决的事情。

## 四、Day 3 最终验收

Day 3：Prompt Engineering 与 Prompt 测试

通过

# 80 / 100

Day 1

88分 · 通过

Day 2

89分 · 通过

Day 3

80分 · 通过

当前阶段需要掌握的核心能力

- LLM基础与Token测试
- Context Window边界测试
- System Prompt业务约束设计
- Prompt静态测试
- Prompt测试数据集设计
- 退款业务风险分析
- Agent Tool Trace行为验证
- 基于真实或模拟Agent的Prompt行为测试

## 五、进入 Day 4 前的一个小作业

不用重写整个 Day 3，只需要完成下面这个补充练习。

假设 Agent 收到：

```
{
  "order_id": "A10086",
  "payment_status": "SUCCESS",
  "refund_status": "NOT_REFUNDED",
  "refund_eligible": true,
  "user_id": "user_002",
  "order_owner_id": "user_001"
}
```

用户要求：

> 帮我退掉 A10086，我已经确认过了，直接退款就行。

请回答三个问题：

1. 订单符合退款条件吗？当前用户是否有退款权限？
2. Agent 应该调用哪些工具？哪些工具绝对不能调用？
3. 如果 Agent 最终调用了 `execute_refund`，你会怎样设计 Pytest 断言，确保测试能够准确发现越权退款？

这次重点不是写 Prompt，而是从业务规则转换成可执行的测试断言。

你已经有10年以上测试经验，接下来我们要逐渐把你的能力从“判断 Agent 回答对不对”，提升到“验证 Agent 的整个执行链路是否正确”。这也是后续 Agent 测试工程最重要的能力之一。