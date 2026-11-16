# 测试编号	测试目标	预期结果
# TC01	历史记忆正确影响 Agent 决策	Agent 能读取相关历史信息
# TC02	Context 信息筛选正确	包含必要信息，排除无关信息
# TC03	Memory 读取异常	Agent 不应因此错误执行退款
# 其中 TC03 特别重要：Memory 服务不可用，不代表 Agent 可以跳过订单查询、权限验证和退款校验。

def test_day13_01_agent_retrieve_context():
    pass


def test_day13_02_agent_retrieve_context():
    pass

def test_day13_03_agent_run_correctly_when_memory_not_work():

    pass