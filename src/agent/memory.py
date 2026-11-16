# 实现一个简单的 AgentMemory 类，至少包含四个方法：
# 方法	功能
# add()	添加记忆
# retrieve()	查询记忆
# update()	更新记忆
# delete()	删除记忆
from typing import Any


class ShortTermMemory:

    def __init__(self):
        self.messages = []
        self.current_task = None
        self.context = {}

    def add_message(self, role, content):
        self.messages.append({
            "role": role,
            "content": content
        })



    def update_context(self, key, value):
        self.context[key] = value

    def retrieve_context(self, key: object) -> Any | None:

        return self.context.get(key)

    def delete_context(self,key):

        return self.context.pop(key,None)


def build_context(memory:ShortTermMemory, required_keys):
    """实现要求
1. 根据 required_keys 提取指定信息。
2. 如果某个 key 不存在，跳过它，不报错。
3. 不提取未指定的 key。
4. 不修改原始 Memory。"""
    result = {}
    for key in required_keys:
        if key in memory.context:
            result[key] = memory.retrieve_context(key)
    return result
