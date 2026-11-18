import json
from dataclasses import asdict
from pathlib import Path

from agent.planning import Step, Plan


class JsonPersistence:

    def __init__(self,storage_dir="src/tem_path"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_checkpoint(self, plan):
        #Agent 在需要保存状态的位置调用
        file_path = self.storage_dir / f"{plan.plan_id}.json"
        temp_path = file_path.with_suffix(".tmp")

        data = asdict(plan)

        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        temp_path.replace(file_path)


    def load_checkpoint(self, checkpoint_id):
        #Agent 恢复时调用
        file_path = self.storage_dir / f"{checkpoint_id}.json"

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


