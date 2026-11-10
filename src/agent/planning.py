from dataclasses import dataclass, field
from typing import Any


@dataclass
class Step:

    step_id: str
    task:str
    depends_on:list[str]=field(default_factory=list)
    status: str = "pending"





@dataclass
class Plan:
    steps: list[Step] = field(default_factory=list)
    status: str = "pending"




