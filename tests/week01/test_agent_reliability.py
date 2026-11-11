
from agent.llm_agent import LLMToolAgent
from tools.order_tool import OrderTool
from tools.refund_tool import RefundTool
from utils.tool import tool_response, text_response, tool_response_exception
from tests.conftest import FakeLLM









class MockOrderTool(OrderTool):
    def query_order(self, order_id: str) -> dict:
        raise Exception("unknown exception error")


class MockRefundTool(RefundTool):
    def execute_refund(self,user_id, order_id: str) -> dict:
        raise Exception("unknown exception error")





def test_tc01_tool_without_arguments_and_args_check_works(env):
    #Tool 参数缺失或类型错误,参数校验是否可靠
    llm = FakeLLM([tool_response_exception("query_order", "ORD1001")])
    agent = LLMToolAgent(llm, env["tools"])
    state = agent.run("U001", "帮我查一下订单 ORD1001")

    # 1. Agent 应返回失败
    assert state.status == "failed"

    # 2. 不应该记录任何工具调用
    assert state.tool_calls == []

    # 3. 应该明确提示参数为空
    assert "arguments must not empty" in state.final_response

    # 4. 只调用一次 LLM，参数校验失败后立即结束
    assert len(llm.calls) == 1





def test_tc02_check_tools_only_run_once(env):
    from unittest.mock import Mock
    # 验证“每个工具真实执行一次”，使用 Mock(wraps=...) 监控工具方法
    query_order = env["tools"]["query_order"]
    permission_check = env["tools"]["permission_check"]
    refund = env["tools"]["execute_refund"]

    query_order.query_order = Mock(wraps=query_order.query_order)
    permission_check.check_permission = Mock(wraps=permission_check.check_permission)
    refund.execute_refund = Mock(wraps=refund.execute_refund)

    #多工具调用及真实执行次数,调用顺序、重复调用
    llm = FakeLLM([tool_response("query_order", "ORD1001"),
                   tool_response("permission_check", "ORD1001"),
                   tool_response("execute_refund", "ORD1001"), text_response("订单 ORD1001 退款成功。")])
    agent = LLMToolAgent(llm, env["tools"])
    state = agent.run("U001", "帮我把订单 ORD1001退款")

    # 1.  工具调用成功
    assert state.status == "success"

    # 2. 工具调用顺序
    assert len(state.tool_calls)==3
    assert state.tool_calls[0]["tool_name"]=="query_order"
    assert state.tool_calls[1]["tool_name"] == "permission_check"
    assert state.tool_calls[2]["tool_name"] == "execute_refund"

    # 3.  LLM被调用4次，没有重复调用
    assert len(llm.calls) == 4

    # 4. 验证 Python 工具真实执行次数
    assert query_order.query_order.call_count == 1
    assert permission_check.check_permission.call_count == 1
    assert refund.execute_refund.call_count == 1




def test_tc03_order_tool_exception(env):
    #Order Tool 抛出异常,Agent是否捕获异常并停止
    llm = FakeLLM([tool_response("query_order", "ORD1001")])
    # 使用MockOrderTool模拟工具返回异常
    tools=env["tools"]
    tools["query_order"]=MockOrderTool()
    agent = LLMToolAgent(llm, tools)
    state = agent.run("U001", "帮我查一下订单 ORD1001")


    assert state.status == "failed"

    # Agent 否捕获异常并停止
    assert "unknown exception error" in state.final_response
    #确实执行了订单查询
    assert state.tool_calls[0]["tool_name"]=="query_order"
    #只记录了一次工具调用
    assert len( state.tool_calls)==1
    #异常后没有继续请求 LLM
    assert len(llm.calls)==1






def test_tc04_refund_tool_exception_and_check_trace(env):
    #Refund Tool 抛出异常时，检查 Agent 是否正确记录 Trace、返回失败，而不是错误地告诉用户退款成功。
    llm = FakeLLM([tool_response("query_order", "ORD1001"),
                   tool_response("permission_check", "ORD1001"),
                   tool_response("execute_refund", "ORD1001"), text_response("订单 ORD1001 退款成功。")])
    # MockRefundTool
    tools=env["tools"]
    tools["execute_refund"]=MockRefundTool(tools["query_order"].orders)


    agent = LLMToolAgent(llm, env["tools"])
    state = agent.run("U001", "帮我把订单 ORD1001退款")
    # 1.返回失败
    assert state.status == "failed"
    #2. Agent 否捕获异常并停止
    assert "unknown exception error" in state.final_response
    # 3.记录 Trace
    assert any(x["type"]=="observation" and x["tool_name"]=="execute_refund"
               and "unknown exception error" in x["result"]["error"] for x in state.trace)

    # 4. 退款异常后立即终止，不再请求 LLM
    assert len(llm.calls) == 3





def test_tc05_llm_return_6_tools_and_check_max_steps_works(env):
    #LLM 连续返回多个工具调用,最大工具调用次数是否真正生效

    from unittest.mock import Mock

    query_order = env["tools"]["query_order"]
    query_order.query_order = Mock(wraps=query_order.query_order)

    dup_tools={
        "tool_calls": [
            {"name": "query_order", "arguments": {"order_id": "ORD1001"}},
            {"name": "query_order", "arguments": {"order_id": "ORD1002"}},
            {"name": "query_order", "arguments": {"order_id": "ORD1003"}},
            {"name": "query_order", "arguments": {"order_id": "ORD1004"}},
            {"name": "query_order", "arguments": {"order_id": "ORD1001"}},
            {"name": "query_order", "arguments": {"order_id": "ORD1002"}}
        ],
        "content": None
    }

    llm = FakeLLM([dup_tools])
    agent = LLMToolAgent(llm, env["tools"])
    state = agent.run("U001", "帮我把订单 ORD1001退款")

    # 1.  工具调用超过最大限制，返回失败
    assert state.status == "failed"

    # 2. 验证max_step最大只执行5此工具调用
    assert len(state.tool_calls)==5
    assert "Maximum tool calling steps reached" in state.final_response

    # 3. LLM 只对话一次
    assert len(llm.calls)==1

    # 监控真实工具执行次数
    assert query_order.query_order.call_count == 5

