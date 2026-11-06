import pytest

from agent.llm_agent import LLMToolAgent
from agent.llm_agent_ai import LLMAgent
from main import permission_tool
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
    refund_tool=RefundTool(order_tool.orders)
    tools={"order":order_tool,"permission":PermissionTool,"refund":refund_tool}
    return {"tools":tools,"orders":order_tool.orders}

response1={
    "tool_calls": [
        {
            "name": "query_order",
            "arguments": {
                "order_id": "A10086"
            }
        }
    ],
    "content": None
}

response2={
    "tool_calls": [],
    "content": "订单 ORD1001 已支付，未退款。"
}

@pytest.mark.parametrize(
    "responses",
    [response1,response2]
)
def test_tc01_query_order_selects_query_tool_with_correct_args(env,responses:[dict]):
    llm=FakeLLM(responses)
    agent=LLMToolAgent(llm,env["tools"])
    agent.run("U001","帮我查一下订单 ORD1001")
