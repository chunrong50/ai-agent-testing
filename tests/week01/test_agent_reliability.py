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

def tool_response_exception(name, order_id):
    return {
    "tool_calls": [
        {
            "name": f"{name}",
            "arguments": {
            }
        }
    ],
    "content": None
}


def test_tc01_tool_without_arguments_and_args_check_works(env):
    #Tool 参数缺失或类型错误,参数校验是否可靠
    llm = FakeLLM([tool_response_exception("query_order", "ORD1001"), text_response("请提供正确的订单号信息。")])
    agent = LLMToolAgent(llm, env["tools"])
    state = agent.run("U001", "帮我查一下订单 ORD1001")

    assert state.status == "failed"
    assert state.tool_calls == []
    assert len(llm.calls) == 1





def test_tc02_4_tools_and_check_tools_only_run_once():
    #多工具调用及真实执行次数,调用顺序、重复调用
    pass

def test_tc03_order_tool_exception():
    #Order Tool 抛出异常,Agent 是否捕获异常并停止
    pass

def test_tc04_refund_tool_exception_and_check_trace():
    #Refund Tool 抛出异常,是否记录失败，是否错误返回成功
    pass


def test_tc05_llm_return_6_tools_and_check_max_steps_works():
    #LLM 连续返回多个工具调用	最大工具调用次数是否真正生效
    pass
