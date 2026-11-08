from copy import deepcopy

import pytest

from agent.llm_agent import LLMToolAgent
from tools.order_tool import OrderTool
from tools.permission_tool import PermissionTool
from tools.refund_tool import RefundTool


class FakeLLM:

    def __init__(self,responses):
        self.responses =list(responses)
        self.calls = []

    def chat(self,message,tools:None):
        self.calls.append({"message":[dict(m) for m in message],"tools":tools})
        return self.responses.pop(0)

SPY_ORDERS={
"ORD1001": {
        "order_id": "ORD1001",
        "user_id": "U001",
        "amount": -100,
        "payment_status": "PAID",
        "refund_status": "NOT_REFUNDED"
    },
    "ORD1002": {
        "order_id": "ORD1002",
        "user_id": "U002",
        "amount": 299.00,
        "payment_status": "UNPAID",
        "refund_status": "NOT_REFUNDED"
    },
}



@pytest.fixture
def env():
    order_tool=OrderTool()
    permission_tool=PermissionTool()
    refund_tool=RefundTool(order_tool.orders)
    tools={"query_order":order_tool,"permission_check":permission_tool,"execute_refund":refund_tool}
    return {"tools":tools,"orders":order_tool.orders}


def env_spy():
    order_tool=OrderTool(SPY_ORDERS)
    permission_tool=PermissionTool()
    refund_tool=RefundTool(order_tool.orders)
    tools={"query_order":order_tool,"permission_check":permission_tool,"execute_refund":refund_tool}
    return {"tools":tools,"orders":order_tool.orders}




def text_response(content):
    return {"tool_calls": [], "content": content}

def tool_response(name,order_id):

    return {
    "tool_calls": [
        {
            "name": f"{name}",
            "arguments": {
                "order_id": f"{order_id}"
            }
        }
    ],
    "content": None
}



def test_tc01_query_order_selects_query_tool_with_correct_args(env):
    llm=FakeLLM([tool_response("query_order","ORD1001"),text_response("订单 ORD1001 已支付，未退款。")])
    agent=LLMToolAgent(llm,env["tools"])
    state=agent.run("U001","帮我查一下订单 ORD1001")

    assert state.status=="success"
    assert state.tool_calls[0]["tool_name"] == "query_order"
    # 确认工具参数正确
    assert state.tool_calls[0]["arguments"] == {
        "order_id": "ORD1001"
    }

    for x in state.tool_calls:
        assert "refund_tool" not in x["tool_name"]

    # 确认 LLM 被调用了两次
    assert len(llm.calls) == 2



def test_tc02_permission_check_and_refund_tool_with_correct_args(env):

    llm=FakeLLM([tool_response("query_order","ORD1001"),
                 tool_response("permission_check","ORD1001"),
                 tool_response("execute_refund","ORD1001"),text_response("订单 ORD1001 退款成功。")])
    agent=LLMToolAgent(llm,env["tools"])
    state=agent.run("U001","帮我把订单 ORD1001退款")

    assert state.status=="success"
    assert state.tool_calls[0]["tool_name"] == "query_order"
    assert state.tool_calls[1]["tool_name"] == "permission_check"
    assert state.tool_calls[2]["tool_name"] == "execute_refund"

    # 确认工具参数正确
    for x in state.tool_calls:
        assert x["arguments"] == {
            "order_id": "ORD1001"
        }
    # 确认 LLM 被调用了两次
    assert len(llm.calls) == 4


def test_tc03_invalid_user_and_must_not_execute_refund(env):
    llm=FakeLLM([tool_response("query_order","ORD1001"),
                 tool_response("permission_check","ORD1001"),
                 tool_response("execute_refund","ORD1001"),
                 text_response("订单 ORD1001 退款失败，当前您不是这个订单的所有者")])
    agent=LLMToolAgent(llm,env["tools"])
    state=agent.run("U002","帮我把订单 ORD1001退款")

    assert state.status=="failed"
    assert state.tool_calls[0]["tool_name"] == "query_order"
    assert state.tool_calls[1]["tool_name"] == "permission_check"
    assert len(state.tool_calls)==2

    assert len(llm.calls) == 2


def test_tc04_unpaid_order_and_must_not_execute_refund(env):
    llm=FakeLLM([tool_response("query_order","ORD1002"),
                 tool_response("permission_check","ORD1002"),
                 tool_response("execute_refund","ORD1002"),
                 text_response("订单 ORD1002 退款失败，订单未付款")])
    agent=LLMToolAgent(llm,env["tools"])
    state=agent.run("U002","帮我把订单 ORD1002退款")

    assert state.status=="failed"
    assert state.tool_calls[0]["tool_name"] == "query_order"
    assert state.tool_calls[1]["tool_name"] == "permission_check"
    assert state.tool_calls[2]["tool_name"] == "execute_refund"
    assert len(state.tool_calls)==3

    assert len(llm.calls) == 3

    for x in state.trace:
        if x["type"]=="observation" and x["tool_name"]=="execute_refund":
            assert x["result"]["success"]==False
            assert "订单未支付，不能退款" in  x["result"]["error"]











def test_tc05_query_status_and_must_not_execute_refund(env):
    llm=FakeLLM([tool_response("query_order","ORD1001"),
                 tool_response("permission_check","ORD1001"),text_response("订单 ORD1001 已支付，未退款。")])
    agent=LLMToolAgent(llm,env["tools"])
    state=agent.run("U001","帮我把查询ORD1001退款状态")

    assert state.status=="success"
    assert state.tool_calls[0]["tool_name"] == "query_order"

    # 确认工具参数正确
    for x in state.tool_calls:
        assert x["arguments"] == {
            "order_id": "ORD1001"
        }
        # 确认 LLM 被调用了两次
    assert len(llm.calls) == 3






def test_tc06_invalid_tool_name_and_must_not_execute(env):
    llm=FakeLLM([tool_response("query_all","ORD1001"),
                 text_response("订单 ORD1001 查询失败。")])
    agent=LLMToolAgent(llm,env["tools"])
    state=agent.run("U001","帮我把查询所有用户订单信息")

    assert state.status=="failed"
    assert state.tool_calls==[]
    assert len(llm.calls) == 1


def test_tc07_invalid_refund_amout_and_must_not_execute():

    llm=FakeLLM([tool_response("query_order","ORD1001"),
                 tool_response("permission_check","ORD1001"),
                 tool_response("execute_refound", "ORD1001"),
                 text_response("订单 ORD1001 退款失败。订单金额不能为负数或者0")])
    env=env_spy() # 模拟查询订单返回订单的信息中，amout金额为-100
    agent=LLMToolAgent(llm,env["tools"])
    state=agent.run("U001","帮我把订单 ORD1001退款")

    assert state.status=="failed"
    assert len(llm.calls) == 3

    for x in state.trace:
        if x["type"] == "observation" and x["tool_name"] == "execute_refund":
            assert x["result"]["success"] == False
            assert "订单金额异常" in x["result"]["error"]