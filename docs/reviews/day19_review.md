## 如何测试 LLM Agent 的可靠性和一致性？

建议回答：
LLM 的输出具有一定随机性，因此单次测试不能充分反映 Agent 的可靠程度。

我会设计 Evaluation Dataset，对相同输入进行多次重复执行，通过 Evaluation Metrics 判断每次输出是否符合预期。

Reliability 通过 Pass 次数与总执行次数的比例衡量；Consistency 则关注相同输入多次执行时输出是否稳定。

两者需要结合评价，因为输出稳定不代表业务判断正确。

 ## 如何设计一个可维护的 Pytest Agent 自动化测试框架？

你可以这样回答：
我会将公共测试对象的初始化统一放在 conftest.py 中，通过 Fixture 和 Factory 管理公共依赖。Factory 默认创建独立的 Agent、FakeLLM 和业务工具，同时允许测试用例注入自定义 Tool 和 LLM 响应，从而支持不同测试场景。对于有状态的业务对象，会注意实例和底层数据的隔离，避免测试之间相互污染。

