import copy
import os
from copy import deepcopy
from typing import Optional

import pytest
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

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



@pytest.fixture
def llm_openai():
    # 1. 加载环境变量
    load_dotenv()

    # 模型初始化
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL"),  # 替换为你实际使用的模型
        temperature=0.1,  # 温度拉低，让大模型严格遵照文档，减少幻觉
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL")
    )
    return llm


@pytest.fixture
def prompt():
    # 7.
    # 编写带强约束的系统提示词（Prompt Template）
    def build_prompt(system_prompt=None):
        system_prompt = (
            "你是一个严谨的企业助手。\n"
            "请根据以下检索到的上下文资料来回答用户的问题。\n"
            "如果你不知道答案，或者资料中没有提及，请直接回答“根据已知信息无法回答”，绝对不允许自行编造。\n\n"
            "上下文资料:\n{context}"
        ) if not system_prompt else (f"{system_prompt}""上下文资料：\n{context}")


        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])

        return prompt

    return build_prompt



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
    def create_agent(llm_responses,order_tool=None,permission_tool=None,refund_tool=None,retriever=None):
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
        agent=LLMPlanAgent(llm,env["tools"],retriever=retriever)

        # 4. 返回 Agent
        return agent,llm,env


    return create_agent