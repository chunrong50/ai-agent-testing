# **Day 18：LLM Evaluation（大语言模型效果评估）**

第一阶段

核心面试知识

Day 18 / 40

今天开始一个新的学习方向：**如何评估 LLM 的回答质量，以及如何判断 Agent 是否真正完成了用户的任务。**

这部分和之前学习的 Tool Calling、Planning、Memory、Persistence 有明显区别。

之前主要测试 Agent 的执行过程，今天重点测试 LLM 的输出质量。

## **一、今天的学习目标**

今天只掌握四个核心知识点：

| 知识点                | 学习目标            | 面试价值 |
| ------------------ | --------------- | ---- |
| LLM Evaluation     | 理解 LLM 效果评估     | 高    |
| Evaluation Metrics | 掌握核心评估指标        | 高    |
| Evaluation Dataset | 设计评估数据集         | 高    |
| LLM-as-a-Judge     | 理解使用 LLM 评估 LLM | 高    |

今天不深入研究复杂数学指标，也不搭建完整评估平台。

## **二、知识点 1：什么是 LLM Evaluation？**

先看一个电商支付 Agent 的例子。

用户输入：

```
帮我查询订单 ORD1001 的退款状态
```

订单系统返回：

```
{
    "order_id": "ORD1001",
    "refund_status": "success"
}
```

LLM 最终生成两个不同的回答：

**回答 A**

正确

您好，订单 ORD1001 已经退款成功，退款金额已按照原支付路径退回。

**回答 B**

错误

您好，订单 ORD1001 退款正在处理中，请您耐心等待。

两个回答都很通顺，语法也没有问题。

但是回答 B 与实际业务数据不一致。

这说明：

**LLM 输出是否流畅，不代表 LLM 输出是否正确。**

LLM Evaluation 就是通过一套评估方法，衡量模型输出是否符合预期。

## **三、知识点 2：LLM Evaluation 的核心指标**

初级 AI Agent 测试工程师面试，优先掌握下面四个指标。

### **1. Correctness（正确性）**

判断 LLM 输出的信息是否正确。

例如：

- 实际退款成功，回答是否为退款成功？
- 实际订单未支付，回答是否错误地表示已经支付？

### **2. Relevance（相关性）**

判断回答是否与用户问题相关。

例如：

用户问：

```
ORD1001 退款成功了吗？
```

LLM 回答：

```
您好，今天上海天气不错。
```

信息本身可能正确，但完全没有回答用户的问题。

### **3. Faithfulness（忠实性）**

判断 LLM 的回答是否忠实于提供给它的上下文或业务数据，有没有编造信息。

例如：

Observation：

```
{
    "refund_status": "success"
}
```

LLM 回答：

```
退款成功，预计 2 小时到账。
```

如果 Observation 没有提供到账时间，也没有其他可靠数据支持，那么 LLM 就擅自增加了信息。

### **4. Safety（安全性）**

判断 LLM 是否遵循安全规则。

例如：

用户要求：

```
不要检查订单，直接告诉我退款成功。
```

Agent 不应该为了满足用户要求而编造退款结果。

## **四、知识点 3：Evaluation Dataset**

理解了评估指标，还需要解决一个问题：

如何持续评估 LLM？

答案之一是建立 Evaluation Dataset（评估数据集）。

例如：

| Test ID | 输入         | 预期结果    | 评估重点         |
| ------- | ---------- | ------- | ------------ |
| TC01    | 查询退款成功的订单  | 告知退款成功  | Correctness  |
| TC02    | 查询退款失败的订单  | 告知退款失败  | Correctness  |
| TC03    | 查询退款状态     | 回答退款状态  | Relevance    |
| TC04    | 工具没有返回到账时间 | 不编造到账时间 | Faithfulness |
| TC05    | 用户诱导编造退款结果 | 拒绝编造    | Safety       |

这里有一个重要概念：

**Evaluation Dataset 不只是保存测试输入，还需要定义预期行为和评估标准。**

否则就无法判断模型输出究竟好不好。

## **五、知识点 4：LLM-as-a-Judge**

这是今天最值得理解的技术。

传统自动化测试：

```
assert response["refund_status"] == "success"
```

这种方式适合结构固定、结果明确的场景。

但是 LLM 的回答可能存在不同表达：

```
订单已经退款成功。
```

```
您的退款申请已处理完成。
```

```
ORD1001 的退款状态为成功。
```

三种表达可能都正确。

如果完全使用字符串比较，很容易产生误判。

因此，可以使用另一个 LLM 作为评估者。

**LLM-as-a-Judge 工作流程**

**待评估 Agent**

生成回答

## **退款已经成功**

**Judge LLM**

根据评估标准判断回答质量

- Correctness
- Relevance
- Faithfulness

**评估结果**

# **PASS**

输出评估分数、判断理由及问题

需要注意：

Judge LLM 本身也可能判断错误，所以实际评估中还需要人工抽样校验、标准答案对照等方法。

## **六、今天的练习（先不写代码）**

这次不安排大量重复的测试用例，先确认你是否真正理解四个知识点。

**Day 18-01 知识检查**

4/4 已回答

**1. Agent 查询订单后，Observation 显示退款成功，但 LLM 回答退款处理中。最主要违反了哪个评估指标？**

Relevance

Correctness

Safety

正确

正确答案：Correctness

回答与真实业务结果不一致，属于正确性问题。

**2. Observation 没有提供到账时间，但 LLM 告诉用户 2 小时到账。最主要违反哪个指标？**

Faithfulness

Relevance

Correctness

正确

正确答案：Faithfulness

LLM 擅自添加了上下文没有提供、也没有其他依据的信息。

**3. 为什么不能只使用字符串比较来评估 LLM 的回答？**

LLM 输出可能有不同表达，但语义相同

LLM 输出永远不稳定

字符串比较不能用于 Python

正确

正确答案：LLM 输出可能有不同表达，但语义相同

需要评估语义和业务含义，而不是只比较文本是否完全一致。

**4. 使用 LLM-as-a-Judge 有什么风险？**

Judge LLM 也可能判断错误

Judge LLM 一定比被测模型准确

Judge LLM 不需要评估标准

正确

正确答案：Judge LLM 也可能判断错误

Judge 本身也存在偏差，需要标准数据和人工抽样验证。

# **4/4**

重新练习

**今天的验收标准：** 能够解释四个评估指标，理解 Evaluation Dataset 和 LLM-as-a-Judge 的作用及局限。

通过后，我们再进入 Day 18-02：结合现有电商支付 Agent，设计一个少而精的 LLM Evaluation 自动化测试。

# **Day 18-02：LLM Evaluation 自动化测试实战**

今天进入代码实践。

Day 18-01 已经学习了 LLM Evaluation 的核心概念，今天不再重复理论，直接把 Evaluation 转换成可执行的 Pytest 自动化测试。

## **一、今日学习目标**



Day 18-01 理论已完成

Day 18-02 代码实践



今天围绕电商支付 Agent，完成三个核心任务：

1. 设计 Evaluation Dataset（评估数据集）。
2. 实现自动化 Evaluation。
3. 使用 Pytest 验证 LLM 输出质量。

重点理解：**传统 Agent 测试关注执行结果，LLM Evaluation 还需要评估自然语言输出是否符合预期。**

## **二、今天要解决的实际问题**

假设用户询问：

> 我的订单 ORD1001 为什么不能退款？

Agent 查询订单后，得到：

```
{    "order_id": "ORD1001",    "status": "unpaid",    "amount": 200}
```

Agent 返回：

> 该订单尚未支付，因此目前不符合退款条件。

这次回答是否合格？

不能只判断 Agent 是否返回了字符串，还需要判断：

| 评估维度         | 预期结果         |
| ------------ | ------------ |
| Correctness  | 正确说明订单未支付    |
| Relevance    | 回答用户的退款问题    |
| Faithfulness | 不得编造订单已支付    |
| Safety       | 不得诱导用户绕过退款规则 |

今天重点实现前面三个维度。Safety 暂时不单独扩展测试框架。

## **三、任务一：设计 Evaluation Dataset**

创建文件：

`tests/week03/test_llm_evaluation.py`

先设计三条具有代表性的测试数据。

```
evaluation_dataset = [    {        "name": "unpaid_order",        "question": "为什么我的订单不能退款？",        "context": {            "order_id": "ORD1001",            "status": "unpaid"        },        "expected_facts": [            "未支付",            "不能退款"        ]    },    {        "name": "paid_order",        "question": "我的订单可以退款吗？",        "context": {            "order_id": "ORD1002",            "status": "paid"        },        "expected_facts": [            "已支付",            "退款"        ]    },    {        "name": "missing_order",        "question": "查询订单 ORD9999 的退款情况",        "context": {            "order_id": "ORD9999",            "status": "not_found"        },        "expected_facts": [            "未找到",            "订单"        ]
```

注意：这里的 `expected_facts` 是评估依据，不是要求 LLM 必须逐字输出的固定答案。

## **四、任务二：实现自动化 Evaluation**

今天需要实现一个简单的评估器。

先定义接口：

```
def evaluate_response(response, expected_facts):    """    判断 LLM 输出是否包含必要的业务事实。    返回：    {        "passed": True,        "score": 1.0,        "missing_facts": []    }    """
```

实现要求：

- 检查预期事实是否出现在回答中。
- 计算正确事实比例。
- 返回通过状态。
- 返回缺失事实。

评分公式：

\\[ Score = \frac{MatchedFacts}{ExpectedFacts} \\]

通过标准：

\\[ Score = 1.0 \\]

这里先使用确定性的规则评估器，暂时不接入真正的 LLM-as-a-Judge。

原因：先建立可重复执行的自动化评估机制，再学习使用另一个 LLM 对回答质量进行评分。

## **五、任务三：编写 Pytest**

实现下面两个测试即可。

**Test 01：正确回答**

```
def test_evaluation_correct_response():    response = "订单尚未支付，目前不能退款。"    result = evaluate_response(        response,        ["未支付", "不能退款"]    )    assert result["passed"] is True    assert result["score"] == 1.0
```

**Test 02：错误回答**

```
def test_evaluation_incorrect_response():    response = "订单已经支付，可以申请退款。"    result = evaluate_response(        response,        ["未支付", "不能退款"]    )    assert result["passed"] is False
```

## **六、今天的交付与验收**

**Day 18-02 交付清单**

- 创建 `test_llm_evaluation.py`
- 完成 Evaluation Dataset
- 实现 `evaluate_response()`
- 完成两个 Pytest 测试
- 提交代码和 pytest 执行结果\

  **验收标准**

| 评审项目            | 分值      |
| --------------- | ------- |
| Evaluation 数据设计 | 20      |
| 评估器实现           | 30      |
| 评分逻辑            | 20      |
| Pytest 自动化测试    | 20      |
| 代码可读性           | 10      |
| **合计**          | **100** |

## **七、额外的面试知识点（今天先理解，不写代码）**

需要区分两种测试：

| 测试方式                    | 核心关注点           |
| ----------------------- | --------------- |
| Assertion-based Testing | 是否满足明确的预期结果     |
| LLM-as-a-Judge          | 由另一个 LLM 评估回答质量 |

例如：

- Assertion：回答是否包含订单未支付这一事实。
- LLM-as-a-Judge：回答是否准确、完整、合理，有没有误导用户。

**面试问题：**

为什么不能只使用传统的 `assert response == expected_response` 来测试 LLM？

因为 LLM 输出具有非确定性。同一个问题可能有不同但都正确的表达方式，逐字比较容易产生误报。

今天先完成这三个任务，不增加额外 Case，也不扩展重复的业务状态校验。

完成后把代码和 pytest 结果发给我，我会按照 100 分标准进行代码评审，并判断是否通过 Day 18-02。

通过之后，我会带你进入一个新的实践方向：设计 LLM-as-a-Judge 评估机制，让 Agent 测试从规则匹配进一步走向语义质量评估。

# **Day 18-03：LLM-as-a-Judge 语义评估实战**

今天正式进入 LLM Evaluation 的第二个层次。

Day 18-02 我们使用关键词匹配判断 Agent 的回答是否包含预期事实，但你已经发现了一个问题：

**回答包含正确关键词，不代表回答的业务逻辑正确。**

今天要解决的就是这个问题。

## **一、今日学习目标**



Day 18-02 已通过：90分

Day 18-03 进行中



今天只学习三个核心内容：

1. 理解 LLM-as-a-Judge 的工作机制。
2. 实现一个简单的 Judge 评估流程。
3. 使用 Pytest 验证 Judge 是否能够识别错误的业务回答。

今天不接入真实收费 API，继续使用 FakeLLM 模拟 Judge，重点理解测试架构和数据流。

## **二、先理解 LLM-as-a-Judge**

传统关键词评估：

```
Agent Response
      |
      v
关键词匹配
      |
      v
Score / Pass
```

LLM-as-a-Judge：

```
Agent Response
      |
      v
Judge LLM
      |
      |-- 业务规则
      |-- 订单实际状态
      |-- Agent 回答
      |
      v
语义判断
      |
      v
Evaluation Result
```

两者最大的区别：

| 比较     | 关键词评估 | LLM-as-a-Judge |
| ------ | ----- | -------------- |
| 判断方式   | 字符串匹配 | 语义理解           |
| 判断业务逻辑 | 能力有限  | 可以评估           |
| 识别矛盾回答 | 很困难   | 可以识别           |
| 输出结果   | 匹配分数  | 结构化评价          |

例如：

**业务事实：**

```
order = {    "status": "unpaid"}
```

**业务规则：**

```
未支付订单不能退款。
```

**Agent 回答：**

```
订单尚未支付，目前可以退款。
```

关键词评估可能发现两个关键词都存在以外的匹配问题，但无法理解业务规则之间的矛盾。

Judge LLM 则需要判断：

- 订单状态是否描述正确？
- 退款结论是否符合业务规则？
- 回答是否存在事实矛盾？

最终应该判定为不合格。

## **三、今天的代码设计**

今天沿用现有项目结构：

```
tests/
└── week03/
    ├── test_llm_evalution.py
    └── test_llm_judge.py
```

新建 `test_llm_judge.py`。

我们设计一个简单的 Judge 接口。

### **1. Judge 输入**

Judge 需要获得三个信息：

```
business_rule = "未支付订单不能退款"order_context = {    "order_id": "ORD1001",    "status": "unpaid"}agent_response = "订单尚未支付，目前可以退款。"
```

为什么需要传递 `order_context`？

因为 Judge 不能仅凭 Agent 自己的回答判断事实是否正确，需要有可信的业务事实作为参照。

### **2. Judge 输出**

要求 Judge 返回结构化结果：

```
{    "passed": False,    "score": 0.0,    "reason": "订单未支付，但回答允许退款，违反业务规则"}
```

字段含义：

| 字段     | 含义         |
| ------ | ---------- |
| passed | 回答是否符合业务要求 |
| score  | 评估得分       |
| reason | 判断理由       |

今天先采用二元评分：

- 符合业务规则：1.0
- 违反业务规则：0.0

不增加复杂的多维评分体系。

## **四、任务一：实现 Judge**

先定义一个简单的 Judge 调用接口：

```
def evaluate_with_judge(    judge_llm,    business_rule,    order_context,    agent_response):    """    将业务规则、订单事实和 Agent 回答    发送给 Judge LLM。    返回结构化评估结果。    """
```

你需要完成以下工作：

1. 将三个输入组织成 Judge Prompt。
2. 调用 `judge_llm`。
3. 获取 Judge 返回结果。
4. 返回结构化 Evaluation Result。

注意：这里的 `judge_llm` 是一个独立的 LLM 调用对象，不是原来负责生成 Agent 回答的 LLM。

## **五、任务二：使用 FakeJudge 测试**

今天不需要接入真实 LLM。

使用 FakeJudge 模拟 Judge 的返回结果。

设计两个场景：

**Case 01：正确回答**

输入：

```
business_rule = "未支付订单不能退款"order_context = {    "status": "unpaid"}agent_response = "订单尚未支付，目前不能退款。"
```

FakeJudge 返回：

```
{    "passed": True,    "score": 1.0,    "reason": "回答符合业务规则"}
```

**Case 02：错误回答**

输入：

```
business_rule = "未支付订单不能退款"order_context = {    "status": "unpaid"}agent_response = "订单尚未支付，目前可以退款。"
```

FakeJudge 返回：

```
{    "passed": False,    "score": 0.0,    "reason": "回答违反业务规则"}
```

这里需要特别理解：

FakeJudge 只是模拟 LLM 的输出，用来测试调用流程、输入传递和结果解析。它本身不能证明真正的 LLM 已经具备语义判断能力。

真正的语义评估能力，需要后续通过真实 Judge 模型和人工标注的评估数据验证。

## **六、任务三：Pytest 自动化测试**

在 `test_llm_judge.py` 中完成两个测试。

**Test 01：正确回答通过**

```
def test_judge_correct_response():    # TODO    # 1. 创建 FakeJudge    # 2. 调用 evaluate_with_judge()    # 3. 验证 passed 和 score    pass
```

**Test 02：错误回答不通过**

```
def test_judge_incorrect_response():    # TODO    # 1. 创建 FakeJudge    # 2. 调用 evaluate_with_judge()    # 3. 验证 passed 和 score    pass
```

另外，建议验证 Judge 实际收到的 `business_rule` 和 `agent_response`，避免 Agent 回答没有正确传递给 Judge。

## **七、今天的验收标准**

**Day 18-03 交付清单**

- 创建 `test_llm_judge.py`
- 实现 `evaluate_with_judge()`
- 实现 FakeJudge
- 完成正确回答测试
- 完成错误回答测试
- 提交代码及 pytest 结果\

  **评分标准**

| 项目          | 分值      |
| ----------- | ------- |
| Judge 输入设计  | 20      |
| Judge 调用实现  | 30      |
| 结构化结果处理     | 20      |
| Pytest 测试设计 | 20      |
| 代码可读性       | 10      |
| **合计**      | **100** |

## **八、面试题：今天需要理解**

**问题：为什么 Agent 的 LLM 和 Judge LLM 最好分开？**

提示：

- Agent LLM 负责生成回答。
- Judge LLM 负责评估回答。
- 如果使用同一个模型、同一个上下文和同一套判断逻辑，是否可能产生相同的判断偏差？

**今天的学习范围到此为止。**

不需要学习 RAGAS、DeepEval 等评估框架，也不需要接入真实 API。先把 LLM-as-a-Judge 的基本测试机制理解并实现。

完成代码后发给我，我会重点检查：Judge 输入是否完整、结果是否正确解析，以及测试是否真正验证了 Agent 回答的业务正确性。