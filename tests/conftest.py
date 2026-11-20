import copy
from copy import deepcopy
from typing import Optional

import pytest

from agent.llm_agent_plan import LLMPlanAgent
from tools.order_tool import OrderTool
from tools.permission_tool import PermissionTool
from tools.refund_tool import RefundTool


class FakeLLM:

    def __init__(self,responses):
        self.responses =list(responses)
        self.calls = []

    def chat(self,message,tools=None):
        self.calls.append({"message":copy.deepcopy(message),"tools":copy.deepcopy(tools)})
        return self.responses.pop(0)

class TimeoutOrderTool(OrderTool):

    def query_order(self, order_id):
        raise TimeoutError("db timeout")


class TimeoutRetryOrderTool(OrderTool):
    def __init__(self,orders: Optional[dict] = None,retry=0):
        super().__init__(orders)
        self.retry=retry

    def query_order(self, order_id):
        if self.retry>0:
            self.retry-=1
            raise TimeoutError("db timeout")
        else:
            #重试成功
            order = self.orders.get(order_id.strip())
            return {
                "success": True,
                "data": deepcopy(order)
            }


def text_response(content):
    # 模拟LLM的文本响应结果
    return {"tool_calls": [], "content": content}

def tool_response(name,order_id):
    # 模拟LLM的响应结果中包含tool_calls，工具调用

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





#负责模拟评估过程
class FakeJudge:
    def __init__(self,response):
        self.response =response
        self.calls = []

    def judge(self,business_rule,order_context,agent_response):
        # 返回{
        #     "passed": True,
        #     "score": 1.0,
        #     "reason": "回答符合业务规则"
        # }
        # 记录收到的参数
        self.calls.append({"business_rule":business_rule,"order_context":order_context,"agent_response":agent_response})

        return self.response



@pytest.fixture
def env():
    order_tool=OrderTool()
    permission_tool=PermissionTool()
    refund_tool=RefundTool(order_tool.orders)
    tools={"query_order":order_tool,"permission_check":permission_tool,"execute_refund":refund_tool}
    return {"tools":tools,"orders":order_tool.orders}


@pytest.fixture
def agent_factory():
    def create_agent(llm_responses,order_tool=None,permission_tool=None,refund_tool=None):
        # 1. 初始化业务工具
        if order_tool is None:
            order_tool = OrderTool()
        if permission_tool is None:
            permission_tool = PermissionTool()

        tools={"query_order":order_tool,"permission_check":permission_tool,"execute_refund":RefundTool(order_tool.orders) if refund_tool is None else refund_tool}
        env={"tools":tools,"orders":order_tool.orders}

        # 2. 初始化 FakeLLM
        llm=FakeLLM(llm_responses)

        # 3. 初始化 Agent
        agent=LLMPlanAgent(llm,env["tools"])

        # 4. 返回 Agent
        return agent,llm,env


    return create_agent