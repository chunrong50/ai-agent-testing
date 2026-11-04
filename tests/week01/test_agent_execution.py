import pytest

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
@pytest.fixture(scope="function")
def agent():
    return PaymentAgent(tools)



def test_normal_query_order(agent):
    # 测试订单查询成功
    result = agent.run(
        user_id="U001",
        user_input="帮我查询订单 ORD1001 的支付状态"
    )
    assert "查询成功" in result.final_response
    assert "ORD1001" in result.final_response
    assert "success" in result.status
    assert "query_order" in result.tool_calls[0]["tool_name"]
    for trace in result.trace:
        assert not (trace.get("type") == "tool_call" and trace.get("tool_name") == "refund_tool")


def test_normal_refund(agent):
    # 测试退款成功
    result = agent.run(user_id="U001",user_input="帮我退款 ORD1001")


    if result.status == "SUCCESS":
        order_id = "ORD1001"
        amout=199.00
        # check 退款结果
        assert order_id in result.final_response
        assert "退款金额" in result.final_response
        assert "199.00" in result.final_response or "199.0" in result.final_response   or "199" in result.final_response
        assert "退款成功" in result.final_response

        # check 工具调用的顺序及传入的参数
        tool_calls=[]
        for tool_call in result.tool_calls:
            tool_calls.append(tool_call.get("tool_name"))
            assert tool_call["arguments"]["order_id"]==order_id

        assert tool_call[0]=="query_order"
        assert tool_call[1] == "check_permission"
        assert tool_call[2]== "refund_tool"

        # check 工具返回的结果
        tool_response ={}
        for trace in result.trace:
            if trace.get("type") == "observation":
                key=trace.get("tool_name")
                tool_response.append(key,trace.get("result"))


        for k,v in tool_response.items():
            assert v.get("success") == True
            if k == "query_order":
                assert v.get("data").get("order_id")==order_id
                assert v.get("data").get("amount") == amout

            elif k == "check_permission":
                assert v.get("allowed")==True
                assert v.get("user_id") == v.get("order_user_id")


            else:
                assert v.get("order_id")==order_id
                assert v.get("refund_amount") == amout
                assert v.get("message") == "退款成功"

    elif result.status == "failed"  :
        #任务失败
        pass
    else:
        # 工具异常
        pass





# {'step': 3, 'type': 'observation', 'tool_name': 'query_order', 'result': {'success': True, 'data': {'order_id': 'ORD1001', 'user_id': 'U001', 'amount': 199.0, 'payment_status': 'PAID', 'refund_status': 'NOT_REFUNDED'}}}
# {'step': 5, 'type': 'observation', 'tool_name': 'check_permission', 'result': {'success': True, 'allowed': True, 'user_id': 'U001', 'order_user_id': 'U001', 'reason': '用户有权操作该订单'}}
#{'step': 7, 'type': 'observation', 'tool_name': 'execute_refund', 'result': {'success': True, 'order_id': 'ORD1001', 'refund_amount': 199.0, 'refund_status': 'REFUNDED', 'message': '退款成功'}}