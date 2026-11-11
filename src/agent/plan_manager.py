"""
PlanManager 暂时只需要实现以下五个方法：
方法	作用
set_plan(plan)	保存 Plan
get_ready_steps()	获取当前允许执行的 Step
mark_running(step_id)	将 Step 标记为执行中
mark_completed(step_id)	将 Step 标记为完成
mark_failed(step_id)	将 Step 标记为失败
"""
from typing import List

from agent.planning import Plan, Step


class PlanManager:

    def __init__(self, plan: Plan):
        self.plan = plan


    # 重新设置plan
    def set_plan(self, plan):
        self.plan = plan



    def get_ready_steps(self) -> List[Step]:
        ready_steps = []

        step_map={step.step_id: step for step in self.plan.steps}

        for step in self.plan.steps:
            # 只考虑等待执行的 Step
            if step.status == "pending":
                if not step.depends_on:
                    ready_steps.append(step)

                else:
                    dependencies_completed=True
                    for dependency_id in step.depends_on:
                        dependency = step_map.get(dependency_id)
                        if dependency is None :
                            dependencies_completed = False
                            break

                        if dependency.status != "completed":
                            dependencies_completed = False
                            break

                    if dependencies_completed:
                        ready_steps.append(step)

        return ready_steps





    def mark_running(self, step_id):
        for step in self.plan.steps:
            if step.step_id == step_id:
                step.status = "running"


    def mark_completed(self, step_id):
        for step in self.plan.steps:
            if step.step_id == step_id:
                step.status = "completed"




    def mark_failed(self, step_id):
        for step in self.plan.steps:
            if step.step_id == step_id:
                step.status = "failed"

