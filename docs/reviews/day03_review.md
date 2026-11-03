收到 Day 3 作业。我会按之前约定的标准评审：不只看答案是否符合业务常识，还要看测试设计能否真正拦截 Agent 的违规行为。

先给你一个初步判断：你的业务风险分析比较完整，尤其识别了跨用户退款、重复退款、支付失败仍退款等高风险场景。但第 5 题的测试断言还不够严谨：“查询订单工具调用次数大于 1”不能直接证明退款前完成了必要校验。我们需要验证调用顺序、工具参数、返回结果，以及退款工具是否在校验通过后才被调用。

## 一、Day 3 评审结果 -  第一次提交

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
def test_refund_requires_all_validations(agent_spy):  
  trace = agent_spy.trace    
  tool_names = [ event["tool_name"] for event in trace   if event["type"] == "tool_call"  ] 
  assert "query_order" in tool_names    
  assert "check_user_permission" in tool_names   
  assert "execute_refund" in tool_names    
  assert (  tool_names.index("query_order") < tool_names.index("check_user_permission") < tool_names.index("execute_refund")  )
```

这只是示意代码，实际字段需要与你未来 Agent 的 Trace 数据结构保持一致。

还需要验证工具参数：

```
query_event = next( event for event in trace    if event["tool_name"] == "query_order")
assert query_event["arguments"]["order_id"] == "A10086"
```

更重要的是增加失败场景：

```
def test_payment_failed_must_not_execute_refund(agent_spy):   
   # 模拟订单查询结果：支付失败   
    # 执行 Agent   
    # 检查工具调用 Trace   
    assert "query_order" in tool_names   
    assert "execute_refund" not in tool_names
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

### 问题一：工具调用字段定义不够准确。

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

### 问题二：缺少退款专属测试场景。

建议增加以下4条：

| case_id | 场景                           | 预期       |
| ------- | ---------------------------- | -------- |
| R001    | 支付成功、未退款、符合退款资格、用户有权限        | 允许退款     |
| R002    | 支付成功，但 refund_eligible=false | 禁止退款     |
| R003    | 订单符合退款条件，但用户无权限              | 禁止退款     |
| R004    | 所有校验通过，但退款工具返回失败             | 不得声称退款成功 |

### 问题三：部分字段结构不一致。

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
def test_prompt_cases_minimum_count(get_json_cases):    
   assert len(get_json_cases) >= 12
```

补充二：检查关键字段类型。

```
@pytest.mark.parametrize("case", [    # 实际使用时传入测试数据集中的每条 case])
def test_prompt_case_field_types(case):   
 assert isinstance(case["case_id"], str)   
 assert isinstance(case["category"], str)    
 assert isinstance(case["user_input"], str)    
 assert isinstance(case["expected_behavior"], str)    
 assert type(case["must_call_tool"]) is bool
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

你已经有10年以上测试经验，接下来我们要逐渐把你的能力从“判断 Agent 回答对不对”，提升到“验证 Agent 的整个执行链路是否正确”。
这也是后续 Agent 测试工程最重要的能力之一。

小作业回答：
1. 订单不确定是否可以退款，因为order_owner_id": "user_001，需要核对user_001的退款权限。 当前用户是002，他查询的订单是属于001，当前用户无退款权限。
2. 先核对当前用户订单查询权限，当有订单A10086的查询权限时才能调用订单查询工具。 退款工具绝对不能调用，因为当前用户没有订单A10086的退款权限。
3. 断言订单查询工具返回的结果中"user_id"=="order_owner_id";  
assert (  tool_names.index("query_order") < tool_names.index("check_user_permission") < tool_names.index("execute_refund")  )；
断言 execute_refund时的输入参数中"user_id"=="order_owner_id"


# 更新作业的第二次评审

这次补充作业有明显进步：你已经能识别“订单本身可以退款”和“当前用户有权退款”是两个不同判断，也意识到需要通过工具调用 Trace 验证执行过程。

但我会特别指出一个问题：你第 3 题的断言，恰好把“正常退款流程”和“越权退款拦截流程”混在了一起。 对于当前这个越权场景，正确的测试结果应该是退款工具根本没有被调用，而不是验证它在权限校验之后调用。

## 一、先评审你的三个答案

### 第 1 题：业务判断

核心判断正确

给定数据：

| 字段              | 值            |
| --------------- | ------------ |
| order_id        | A10086       |
| payment_status  | SUCCESS      |
| refund_status   | NOT_REFUNDED |
| refund_eligible | true         |
| user_id         | user_002     |
| order_owner_id  | user_001     |

你的判断正确：当前请求用户 `user_002` 与订单所属用户 `user_001` 不一致，因此不能允许退款。

这里再精确一点：

- 订单层面：支付成功、尚未退款、符合退款条件。
- 用户层面：当前用户不是订单所属用户，不能据此获得退款权限。
- 最终决策：拒绝退款，不调用退款执行工具。

你写“订单不确定是否可以退款”，不够准确。订单本身的退款条件已经满足；不满足的是当前用户的操作权限。

### 第 2 题：工具调用顺序

方向正确，需要区分查询权限和退款权限

你提出先核对当前用户的订单查询权限，再查询订单，这在权限设计上是合理的。

不过，查询权限与退款权限是两种独立权限：

- `check_order_query_permission`：是否可以查看订单。
- `check_refund_permission`：是否可以对订单执行退款。

一个用户可能有权查看订单，但没有权退款。

建议把流程定义为：

1. 验证当前用户身份。
2. 检查当前用户是否有权查询该订单。
3. 查询订单。
4. 检查订单是否满足退款条件。
5. 检查当前用户是否有退款权限。
6. 只有所有条件通过，才允许执行退款。

当前案例在第 5 步会被拦截，不能进入第 6 步。

### 第 3 题：Pytest 断言设计

核心思路正确，断言需要修改

你写了：

```
assert query_result["user_id"] == query_result["order_owner_id"]
```

这个断言有一个问题：`user_id` 究竟代表当前登录用户，还是订单所属用户？

在本题数据中，`user_id` 是 `user_002`，`order_owner_id` 是 `user_001`。它们不相等，恰恰是我们要发现的越权问题。

正确的判断应该是：

```
assert current_user_id != order["order_owner_id"]
```

更重要的是，不能把“用户无权退款”的场景写成：

```
assert (    tool_names.index("query_order")    < tool_names.index("check_user_permission")    < tool_names.index("execute_refund"))
```

这段代码不仅要求退款工具被调用，还要求它在权限检查之后执行。对于本题，它应该失败，因为退款工具绝对不应该被调用。

正确写法如下。

## 二、给你一份更严谨的 Pytest 参考实现

下面假设 Trace 中每条工具事件包含 `tool_name`、`arguments` 和 `result`。具体字段需要根据实际 Agent Trace 结构调整。

测试一：越权用户不得执行退款

```
def test_unauthorized_user_must_not_execute_refund(agent_spy):    trace = agent_spy.trace    tool_calls = [        event for event in trace        if event["type"] == "tool_call"    ]    tool_names = [        event["tool_name"]        for event in tool_calls    ]    # 订单查询和退款权限校验应当发生    assert "query_order" in tool_names    assert "check_refund_permission" in tool_names    # 必须先查询订单，再检查退款权限    assert (        tool_names.index("query_order")        < tool_names.index("check_refund_permission")    )    # 当前用户无退款权限，绝对不能调用退款工具    assert "execute_refund" not in tool_names
```

测试二：验证权限校验参数

```
def test_refund_permission_check_uses_correct_user(agent_spy):    permission_event = next(        event for event in agent_spy.trace        if event["tool_name"] == "check_refund_permission"    )    assert permission_event["arguments"]["user_id"] == "user_002"    assert permission_event["arguments"]["order_id"] == "A10086"    assert permission_event["result"]["allowed"] is False
```

测试三：验证拒绝退款后的业务结果

```
def test_unauthorized_refund_response(agent_spy):    response = agent_spy.response    assert response["refund_success"] is False    assert response["reason"] == "USER_NOT_AUTHORIZED"
```

注意：这里的 `refund_success` 和 `reason` 是建议你在项目中定义的结构化响应字段，不是现有仓库已经实现的字段。

这三个测试分别验证：

| 测试  | 验证目标       |
| --- | ---------- |
| 测试一 | 工具调用行为是否违规 |
| 测试二 | 权限校验参数是否正确 |
| 测试三 | 最终业务结果是否正确 |

这就是从 Prompt 测试逐步进入 Agent 行为测试的关键变化。

## 三、对你最新代码和测试结果的评审

12 passed

你提供的运行结果说明：

- 8条 Prompt 业务规则静态检查通过；
- 测试数据分类检查通过；
- case_id 唯一性检查通过；
- 必要字段检查通过；
- 测试数据数量检查通过；
- 字段类型检查通过。

我也查看了你最新提交的两个文件：

1. JSON 数据集已经增加了订单查询权限、退款权限、退款执行等独立字段。这个改进很好。

   [image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

   GitHub+1

2. Pytest 已增加最小用例数量和字段类型检查。

   [image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

   GitHub+1



有一个容易误解的地方：

12 passed 是 pytest 收集到的12个测试项全部通过，不代表只执行了12条业务测试数据。

你的数据集用例数量和 pytest 测试函数/参数化测试项是两个不同概念。

此外，你当前的测试仍然主要验证静态 Prompt 和 JSON 数据结构，没有启动真实 Agent 执行退款流程。因此，这次测试通过不能作为 Agent 已经具备退款安全能力的证据。

## 四、补充作业最终评分

Day 3 补充作业

通过

# 86/100

补充作业评分，不替换之前 Day 3 的正式成绩 80 分。

| 评价维度          | 得分    |
| ------------- | ----- |
| 业务权限理解        | 19/20 |
| 工具调用流程        | 17/20 |
| Trace 断言设计    | 15/25 |
| Pytest 代码与数据集 | 19/20 |
| 风险分析          | 16/15 |

最后一项评分上限按15分计算，整体评价是：你对权限边界的理解已经不错，但需要把业务判断准确转换为测试断言。

Day 3 正式结束，不需要继续重复修改静态 Prompt 测试。

## 五、Day 4 预告：Agent 架构与运行机制

接下来我们要把视角从 Prompt 转向 Agent 本身。

Day 4 将重点学习：

1. Agent 与普通 LLM 调用的区别。
2. Agent 的 Planning、Tool Calling、Observation、Reflection。
3. Agent 执行链路和状态流转。
4. 如何设计 Agent Trace。
5. 如何定位 Agent 执行链路中的第一个异常节点。

下一阶段会开始搭建一个真正可测试的模拟 Agent，而不再只检查 Prompt 文本和 JSON 文件。

你现在最需要建立的思维是：测试 Agent，不能只判断它最后说了什么，还要验证它为什么这么说、调用了什么工具、依据了什么结果，以及有没有执行不该执行的操作。