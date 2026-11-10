
    # def execute(self,step: Step):
    #     if not step.depends_on:
    #         if step.status == "completed":
    #             print(f"{step.task} 已完成.")
    #         else:
    #             print(f"{step.task} 进行中...")
    #             step.status = "running"
    #             print(f"{step.task} 已完成.")
    #             step.status= "completed"
    #     else:
    #         for step in step.depends_on:
    #             self.execute(step)
    #             step.status="completed"
    #
    #
    # def task_plan(self):
    #     for step in self.steps:
    #         self.execute(step)
    #         step.status = "completed"
    #     self.status = "completed"