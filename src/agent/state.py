
""" 保存Agent执行过着"""

# src/agent/state.py

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class AgentState:
    """保存一次 Agent 执行过程中的状态。"""

    user_id: str
    user_input: str

    # 这两行是"可选字段"，用于订单相关场景，没用到时保持 None
    order_id: Optional[str] = None
    order_data: Optional[dict[str, Any]] = None

    # 记录实际发生的工具调用
    tool_calls: list[dict[str, Any]] = field(default_factory=list)

    # 记录完整执行轨迹
    trace: list[dict[str, Any]] = field(default_factory=list)

    final_response: Optional[str] = None

    # running / success / failed
    status: str = "running"

    error: Optional[str] = None

    def add_tool_call(
        self,
        tool_name: str,
        arguments: dict[str, Any]
    ) -> None:
        """记录一次工具调用，把工具名称和参数追加到tool_calls"""

        self.tool_calls.append({
            "tool_name": tool_name,
            "arguments": arguments.copy()
        })

    def add_trace(
        self,
        step_type: str,
        **details: Any
    ) -> None:
        """记录一次执行轨迹。"""

        self.trace.append({
            "step": len(self.trace) + 1,
            "type": step_type,
            **details
        })


a=AgentState("User0001","帮我查询订单A10086")
b=AgentState("User0002","帮我查询订单A10089")
# a.tool_calls=
print(a.status)
print(b.status)
a.add_tool_call("query",{"id": "A10086"})
print(a.tool_calls)
print(b.tool_calls)