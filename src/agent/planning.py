from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Step:

    step_id: str
    task:str
    depends_on:list[str]=field(default_factory=list)
    status: str = "pending"
    order_id: Optional[str] = None
    retry_count: int = 0
    result: Optional[Any] = field(default_factory=dict)





@dataclass
class Plan:
    steps: list[Step] = field(default_factory=list)
    status: str = "pending"
    plan_id: str = ""




