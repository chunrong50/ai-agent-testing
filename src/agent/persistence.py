import json
from dataclasses import asdict
from pathlib import Path

from agent.planning import Step, Plan
from agent.state import AgentState


class JsonPersistence:

    def __init__(self,storage_dir="src/tem_path"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_checkpoint(self, state:AgentState|Plan):
        #Agent 在需要保存状态的位置调用
        name=""
        if isinstance(state, AgentState):
            name = f"state_{state.task_id}"
        if isinstance(state, Plan):
            name = state.plan_id
        file_path = self.storage_dir / f"{name}.json"
        temp_path = file_path.with_suffix(".tmp")

        data = asdict(state)

        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        temp_path.replace(file_path)



    def load_plan(self, plan_id):
        #Agent 恢复时调用
        file_path = self.storage_dir / f"{plan_id}.json"

        if not file_path.exists():
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        steps = [
            Step(**step_data)
            for step_data in data.pop("steps")
        ]

        return Plan(
            steps=steps,
            **data
        )

    def load_state(self, task_id):
        #Agent 恢复时调用
        file_path = self.storage_dir / f"state_{task_id}.json"

        if not file_path.exists():
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        user_id=data.pop("user_id")
        user_input=data.pop("user_input")

        return AgentState(
            user_id=user_id,
            user_input=user_input,
            **data
        )
