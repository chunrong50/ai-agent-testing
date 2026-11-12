from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Step:

    step_id: str
    task:str
    depends_on:list[str]=field(default_factory=list)
    status: str = "pending"
    order_id: Optional[str] = None





@dataclass
class Plan:
    steps: list[Step] = field(default_factory=list)
    status: str = "pending"




