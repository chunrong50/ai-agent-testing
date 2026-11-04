import pytest

from src.agent.agent import PaymentAgent
from src.tools.order_tool import OrderTool
from src.tools.permission_tool import PermissionTool
from src.tools.refund_tool import RefundTool




@pytest.fixture(scope="function")
def agent():
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

    # 5. 创建并返回 Agent
    return PaymentAgent(tools)



def test_normal_query_order(agent):
    # 测试订单查询成功
    result = agent.run(user_id="U001", user_input="帮我查询订单 ORD1001 的支付状态")

    assert result.status == "success"
    assert "查询成功" in result.final_response
    assert "ORD1001" in result.final_response

    # 只应调用一次 query_order，不应触发权限/退款
    tool_names = [c["tool_name"] for c in result.tool_calls]
    assert tool_names == ["query_order"]


    assert not any(t.get("type") == "tool_call" and t.get("tool_name")=="execute_refund" for t in result.tool_calls)


def test_normal_refund(agent):
    # 测试退款成功
    result = agent.run(user_id="U001",user_input="帮我退款 ORD1001")

    order_id = "ORD1001"
    amount=199.00
    # 退款结果
    assert result.status == "success"
    assert order_id in result.final_response
    assert "退款金额" in result.final_response
    assert "退款成功" in result.final_response

    #  工具调用的顺序及传入的参数
    tool_names = [c["tool_name"] for c in result.tool_calls]
    assert tool_names == ["query_order", "check_permission", "execute_refund"]
    for call in result.tool_calls:
        assert call["arguments"]["order_id"] == order_id

    # 工具返回的结果

    observations={ t["tool_name"]:t["result"] for t in result.trace if t.get("type") == "observation"}

    for name,resp in observations.items():
        assert resp.get("success") is True
        if name == "query_order":
            data=resp.get("data")
            assert data["order_id"]==order_id
            assert data["amount"] == amount
            assert data["payment_status"] == "PAID"
            assert data["refund_status"] == "NOT_REFUNDED"

        elif name == "check_permission":
            assert resp["allowed"] is True
            assert resp["user_id"]== resp["order_user_id"]=="U001"
            assert resp["reason"] == "用户有权操作该订单"


        elif name == "execute_refund":
            assert resp["order_id"]==order_id
            assert resp["refund_amount"] == amount
            assert resp["refund_status"] == "REFUNDED"
            assert resp["message"] == "退款成功"





@pytest.mark.parametrize(
    "user_input, expected",
    [
        # 正例：退款语义
        ("帮我退款 ORD1001", True),
        ("把这个订单退掉", True),
        ("我要退还货款", True),
        ("取消订单 ORD1001", True),
        # 反例：查询语义，含"退款"但不该退
        ("查询订单 ORD1001 的支付状态", False),
        ("查询退款状态", False),
        ("订单 ORD1001 退款成功了吗", False),
        ("订单 ORD1001 的退款状态是什么", False),
        # 反例：完全无关
        ("你好", False),
    ],
    ids=["refund", "tui_diao", "tui_huan", "cancel", "query_pay", "query_refund_status", "query_refund_success", "query_refund_status2", "hello"],
)
def test_is_refund_intent(agent,user_input, expected):
    assert agent.is_refund_intent(user_input) is expected



def test_query_refund_status(agent):
    # 查询退款状态
    result = agent.run(user_id="U001", user_input="帮我查询订单 ORD1001 的退款状态")

    assert result.status == "success"
    assert "查询成功" in result.final_response
    assert "NOT_REFUNDED" in result.final_response

    # 只应调用一次 query_order，不应触发权限/退款
    tool_names = [c["tool_name"] for c in result.tool_calls]
    assert tool_names == ["query_order"]

    assert not any(t.get("type") == "tool_call" and t.get("tool_name") == "execute_refund" for t in result.tool_calls)

def test_must_not_query(agent):
    # 无权限查询其他人订单
    result = agent.run(user_id="U002", user_input="帮我查询 ORD1001")

    assert result.status == "failed"
    assert "订单ORD1001不属于当前用户U002" in result.final_response

    # 只应调用一次 query_order，不应触发权限/退款
    tool_names = [c["tool_name"] for c in result.tool_calls]
    assert tool_names == ["query_order"]



def test_must_not_refund(agent):
    # 无权限退款
    result = agent.run(user_id="U002", user_input="帮我退款 ORD1001")

    assert result.status == "failed"
    assert "订单ORD1001不属于当前用户U002" in result.final_response

    # 只应调用一次 query_order，不应触发权限/退款
    tool_names = [c["tool_name"] for c in result.tool_calls]
    assert tool_names == ["query_order"]

    assert not any(t.get("type") == "tool_call" and t.get("tool_name") == "execute_refund" for t in result.tool_calls)


def test_unpaid_must_not_refund_(agent):
    # 未支付不能退款
    result = agent.run(user_id="U002", user_input="帮我退款 ORD1002")

    assert result.status == "failed"


    # 只应调用query_order，check_permission
    tool_names = [c["tool_name"] for c in result.tool_calls]
    assert tool_names == ["query_order","check_permission","execute_refund"]




def test_must_not_double_refund(agent):
    # 已退款订单不能重复退款。
    result = agent.run(user_id="U001", user_input="帮我退款 ORD1003")

    assert result.status == "failed"
    assert "退款失败" in result.final_response
    assert "不能重复退款" in result.final_response
    # 只应调用query_order，check_permission
    tool_names = [c["tool_name"] for c in result.tool_calls]
    assert tool_names == ["query_order","check_permission","execute_refund"]


def test_user_cannot_query_other_users_order(agent):
    result = agent.run(
        user_id="U002",
        user_input="查询订单 ORD1001 的支付状态"
    )

    assert result.status == "failed"
    assert "不属于当前用户" in result.final_response

    # 不应继续调用权限工具或退款工具
    tool_names = [
        item["tool_name"]
        for item in result.tool_calls
    ]

    assert tool_names == ["query_order"]

    # 不应该向用户返回订单的支付、退款信息
    assert "PAID" not in result.final_response
    assert "NOT_REFUNDED" not in result.final_response