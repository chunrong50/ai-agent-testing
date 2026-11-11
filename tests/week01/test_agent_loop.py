

"""
保留以下 4 个测试：
测试	验证的技术能力
正常多轮执行	Tool Call → Observation → Final Answer
直接返回答案	不需要工具时正常结束
超过最大执行轮数	max_steps 能阻止无限循环
工具执行失败	Agent 能识别和处理工具异常
"""
import json

from agent.llm_agent import LLMToolAgent
from tests.conftest import FakeLLM
from utils.tool import tool_response, text_response


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
    # 确认 LLM 被调用了两次
    assert len(llm.calls) == 2


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


def test_tc03_llm_can_get_last_tool_result(env):
    # 实现一个 FakeLLM 连续返回两轮不同响应的 Agent，并验证第二轮 LLM 能够获取第一轮 Tool 的执行结果。
    llm = FakeLLM([tool_response("query_order", "ORD1001"),
                   tool_response("permission_check", "ORD1001"),
                   text_response("订单查询成功，当前用户有权访问。")])
    agent = LLMToolAgent(llm, env["tools"])
    state = agent.run("U001", "帮我看一下查询订单 ORD1001")

    assert state.status == "success"
    assert len(llm.calls) == 3
    assert "订单查询成功" in state.final_response


    tool_result={
        "order_id": "ORD1001",
        "user_id": "U001",
        "amount": 199.00,
        "payment_status": "PAID",
        "refund_status": "NOT_REFUNDED"
    }

    # 第二轮 LLM 请求能够拿到第一轮的 Observation
    assert json.dumps(tool_result) in llm.calls[1]["message"][3]["content"]

    permission_result = {"success": True, "allowed": True, "user_id": "U001", "order_user_id": "U001", "reason": "用户有权操作该订单"}

    # 第三轮 LLM 请求能够拿到第二轮的 Observation
    acutal_permission_result = json.loads(llm.calls[2]["message"][-1]["content"])
    assert permission_result==acutal_permission_result

