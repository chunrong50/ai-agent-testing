面试官：如何测试 LLM Agent 的可靠性和一致性？

建议回答：
LLM 的输出具有一定随机性，因此单次测试不能充分反映 Agent 的可靠程度。

我会设计 Evaluation Dataset，对相同输入进行多次重复执行，通过 Evaluation Metrics 判断每次输出是否符合预期。

Reliability 通过 Pass 次数与总执行次数的比例衡量；Consistency 则关注相同输入多次执行时输出是否稳定。

两者需要结合评价，因为输出稳定不代表业务判断正确。