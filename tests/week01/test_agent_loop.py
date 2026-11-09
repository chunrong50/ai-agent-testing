

"""
保留以下 4 个测试：
测试	验证的技术能力
正常多轮执行	Tool Call → Observation → Final Answer
直接返回答案	不需要工具时正常结束
超过最大执行轮数	max_steps 能阻止无限循环
工具执行失败	Agent 能识别和处理工具异常
"""
import unittest

import pytest

from agent.llm_agent import LLMToolAgent
from tests.week01.test_agent_reliability import tool_response, text_response
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



@pytest.fixture
def env():
    order_tool=OrderTool()
    permission_tool=PermissionTool()
    refund_tool=RefundTool(order_tool.orders)
    tools={"query_order":order_tool,"permission_check":permission_tool,"execute_refund":refund_tool}
    return {"tools":tools,"orders":order_tool.orders}



def test_tc01_normal_turns(env):
    # 正常多轮执行	Tool Call → Observation → Final Answer
    llm = FakeLLM([tool_response("query_order", "ORD1001"), text_response("订单 ORD1001 已支付，未退款。")])
    agent = LLMToolAgent(llm, env["tools"])
    state = agent.run("U001", "帮我查一下订单 ORD1001")

    assert state.status == "success"

    # 确认工具
    assert state.tool_calls[0]["tool_name"] == "query_order"
    assert state.tool_calls[0]["arguments"] == {
        "order_id": "ORD1001"
    }

    # 确认工具的结果
    assert any(x["type"]=="observation" and x["tool_name"]=="query_order" and x["result"]["success"]==True for x in state.trace)

    # 确认 订单 ORD1001 已支付，未退款在final_response
    assert "订单 ORD1001 已支付，未退款" in state.final_response


def test_tc02_no_tool_calls_return_answer(env):
    from unittest.mock import Mock
    # 验证“每个工具真实执行一次”，使用 Mock(wraps=...) 监控工具方法
    query_order = env["tools"]["query_order"]
    permission_check = env["tools"]["permission_check"]
    refund = env["tools"]["execute_refund"]
    query_order.query_order = Mock(wraps=query_order.query_order)
    permission_check.check_permission = Mock(wraps=permission_check.check_permission)
    refund.execute_refund = Mock(wraps=refund.execute_refund)

    llm = FakeLLM([text_response("请问要看上面内容。")])
    agent = LLMToolAgent(llm, env["tools"])
    state = agent.run("U001", "您好，帮我看一下")

    assert state.status == "success"
    # 确认工具没执行
    assert len(state.tool_calls)==0
    assert "请问要看上面内容" in state.final_response

    assert query_order.query_order.call_count==0
    assert permission_check.check_permission.call_count==0
    assert refund.execute_refund.call_count==0


def test_tc03(env):
    # 实现一个 FakeLLM 连续返回两轮不同响应的 Agent，并验证第二轮 LLM 能够获取第一轮 Tool 的执行结果。
    pass
