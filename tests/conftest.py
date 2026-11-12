import pytest

from agent.plan_manager import PlanManager
from agent.planning import Plan
from tools.order_tool import OrderTool
from tools.permission_tool import PermissionTool
from tools.refund_tool import RefundTool
from schemas.tool_schemas import get_schema



class FakeLLM:

    def __init__(self,responses):
        self.responses =list(responses)
        self.calls = []

    def chat(self,message,tools=None):
        self.calls.append({"message":[dict(m) for m in message],"tools":tools})
        return self.responses.pop(0)

class TimeoutOrderTool(OrderTool):
    def query_order(self, order_id):
        raise TimeoutError("db timeout")


@pytest.fixture
def env_timeout_order_tool():
    order_tool=TimeoutOrderTool()
    permission_tool=PermissionTool()
    refund_tool=RefundTool(order_tool.orders)
    tools={"query_order":order_tool,"permission_check":permission_tool,"execute_refund":refund_tool}
    return {"tools":tools,"orders":order_tool.orders}



@pytest.fixture
def env():
    order_tool=OrderTool()
    permission_tool=PermissionTool()
    refund_tool=RefundTool(order_tool.orders)
    tools={"query_order":order_tool,"permission_check":permission_tool,"execute_refund":refund_tool}
    return {"tools":tools,"orders":order_tool.orders}