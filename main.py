
# main.py

from src.agent.agent import PaymentAgent
from src.tools.order_tool import OrderTool
from src.tools.permission_tool import PermissionTool
from src.tools.refund_tool import RefundTool


# 1. 创建订单工具
order_tool = OrderTool()

# 2. 创建权限工具
permission_tool = PermissionTool()

# 3. 创建退款工具
# 注意：和 OrderTool 共用同一份订单数据
refund_tool = RefundTool(
    orders=order_tool.orders
)

# 4. 将工具注册给 Agent
tools = {
    "order": order_tool,
    "permission": permission_tool,
    "refund": refund_tool
}

# 5. 创建 Agent
agent = PaymentAgent(tools=tools)


# 6. 测试订单查询
result = agent.run(
    user_id="U001",
    user_input="帮我查询订单 ORD1001 的支付状态"
)

print("最终回答：", result.final_response)
print("执行状态：", result.status)
print("工具调用：", result.tool_calls)
print("执行轨迹：", result.trace)


# 7. 测试退款
result = agent.run(
    user_id="U001",
    user_input="帮我退款 ORD1001"
)

print("\n退款结果：", result.final_response)
print("执行状态：", result.status)
print("执行轨迹：", result.trace)
