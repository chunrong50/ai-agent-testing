# 沉淀知识点

## AI Agent 测试用例模板：

设计 AI Agent 测试用例时，建议固定使用这个模板：

| 测试项目                    | 内容          |
| ----------------------- | ----------- |
| Test Scenario           | 测试什么场景      |
| Preconditions           | 前置条件和测试数据   |
| User Input              | 用户输入        |
| Expected Tool Call      | 预期工具调用      |
| Expected Tool Result    | 预期工具返回      |
| Expected Agent Response | 预期 Agent 回复 |
| Assertions              | 自动化断言       |
| Trace Evidence          | 执行链路证据      |
| Defect Classification   | 缺陷分类        |



### 需要掌握的五个核心概念
1. 什么是 LLM？

LLM（Large Language Model）是通过大量数据训练得到的语言模型，能够理解和生成自然语言。

2. 为什么 LLM 会产生幻觉？

大模型生成内容的本质是基于模型计算，预测后续 Token，而不是直接查询一个绝对可靠的事实数据库。

因此可能出现：
- 编造订单信息。
- 编造商品价格。
- 错误解释退款规则。
- 给出不存在的 API。
- 将不确定的信息说得非常肯定。
这就是 Hallucination（幻觉）。

测试人员需要验证的是：当模型缺乏可靠依据时，是否会明确表达不确定性，而不是编造答案。

3. 什么是 Token？

Token 是模型处理文本时使用的基本单位。

Token 不完全等于汉字、英文单词或者字符。

Token 数量会影响：
- 输入成本。
- 输出成本。
- 上下文长度。
- 模型处理时间。

4. 什么是 Context Window？

上下文窗口是模型一次请求能够处理的上下文容量。

例如，用户和 Agent 进行了很长时间的对话，可能出现：
- 前面提到的订单号丢失。
- 退款条件遗忘。
- 用户身份信息混淆。
- 前后回答不一致。
这些都是测试需要覆盖的场景。

5. 什么是 Temperature？

Temperature 影响模型输出的随机性。

一般来说，较低的 Temperature 倾向于更稳定的输出；较高的 Temperature 可能带来更多样化的输出。

但它不等于正确率，也不保证低 Temperature 下的结果绝对一致。