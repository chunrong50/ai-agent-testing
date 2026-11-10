"""
PlanManager 暂时只需要实现以下五个方法：
方法	作用
set_plan(plan)	保存 Plan
get_ready_steps()	获取当前允许执行的 Step
mark_running(step_id)	将 Step 标记为执行中
mark_completed(step_id)	将 Step 标记为完成
mark_failed(step_id)	将 Step 标记为失败
"""
from agent.planning import Plan, Step


class PlanManager:

    def __init__(self, plan: Plan,ready_step:str=None,completed_steps:list[Step]=[]):
        self.plan = plan
        self.ready_step = ready_step if ready_step else self.plan.steps[0].step_id
        self.completed_steps = completed_steps

    # 重新设置plan
    def set_plan(self, plan):
        for step in plan.steps:
            if step in self.completed_steps:
                plan.pop(step)



    def get_ready_steps(self):
        for step in self.plan.steps:
            if step.status == "completed":
                self.completed_steps.append(step)
                continue
            elif step.status == "pending" and not step.depends_on:
                self.ready_step=step.step_id
                return self.ready_step
            elif step.status == "pending" and step.depends_on:
                for step_id in step.depends_on:
                    if step_id not in self.completed_steps:
                        self.ready_step = step_id
                        return self.ready_step

        return  self.ready_step


    def mark_running(self, step_id):
        for step in self.plan.steps:
            if step.step_id == step_id:
                step.status = "running"


    def mark_completed(self, step_id):
        flag=False
        for step in self.plan.steps:
            if flag:
                self.ready_step=step.step_id
                break
            if step.step_id == step_id:
                step.status = "completed"
                flag=True
                self.completed_steps.append(step)



    def mark_failed(self, step_id):
        for step in self.plan.steps:
            if step.step_id == step_id:
                step.status = "failed"

    def mark_skipped(self, step_id):
        for step in self.plan.steps:
            if step.step_id == step_id:
                step.status = "skipped"
