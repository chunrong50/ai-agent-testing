
""" 保存Agent执行过着"""

# src/agent/state.py

from dataclasses import dataclass, field
from typing import Any, Optional
from uuid import uuid4


@dataclass
class AgentState:
    """保存一次 Agent 执行过程中的状态。"""

    user_id: str
    user_input: str

    # day09 新增字段，为了不影响之前的cases，使用Optional
    # task_id 能够区分不同任务。
    # current_step 记录当前执行步骤。
    # step_states 保存每个 Step 的状态。
    # step_results 保存每个 Step 的执行结果。

    # 每个任务自动生成唯一 ID
    task_id: str = field(default_factory=lambda: str(uuid4()))
    current_step: Optional[str] = None

    step_states: dict[str, Any] = field(default_factory=dict)
    step_results: list[dict[str, Any]] = field(default_factory=list)


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
        """记录一次工具尝试调用，把工具名称和参数追加到tool_calls"""

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

