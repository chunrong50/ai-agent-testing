
# 关于@dataclass需要注意的点
 ## 普通类：

```
class A:
    x = []          # 类属性，可变 → 所有实例共享
    y = "running"   # 类属性，不可变 → 名义上共享，但无法原地修改，安全
```
可变类属性（list/dict/set）：共享，有坑。

不可变类属性（str/int/None/tuple）：名义上也是类属性、所有实例通过类查找拿到同一个对象，但因为不可变，没人能原地改它，所以实际安全。

 ## @dataclass：

``` 
@dataclass
class A:
    x: list = []                      # 直接报错 ValueError
    x: list = field(default_factory=list)   # 正确，每实例独立
    y: str = "running"                # 正确，每实例独立（默认值不可变）
```
可变默认值写 = []：dataclass 在定义类时就抛 ValueError，根本不让你运行，所以不存在"共享"这回事——它被拦住了。

用 field(default_factory=list)：每个实例创建时调用一次 list()，各自独立。

不可变默认值 = "running"：dataclass 生成 __init__ 默认参数，每个实例拿到自己的属性，独立。

**一句话记忆**
普通类：可变类属性 → 共享（坑）；正确做法是写进 __init__。
dataclass：可变默认值 → 直接报错；必须用 default_factory，结果是每实例独立，没有共享问题。
所以"共享"是普通类里可变类属性的问题，不是 dataclass 的字段特性。dataclass 用报错 + default_factory 把这个问题从源头堵住了。




# 一、`Protocol` 是什么

`Protocol` 是 Python 3.8+ 引入的**结构化子类型（structural subtyping）**机制，也就是"鸭子类型"的静态检查版本。它的核心思想是：

> 只要一个类**拥有某些方法/属性**，它就"符合"这个协议，**不需要显式继承**。
> 这是 Python 的 **`Protocol`（协议）** 用法，`...`（省略号）表示**方法体留空**，这里刻意不实现方法体是有明确目的的。

对比一下两种写法：

```python
# 传统抽象基类：子类必须显式继承
class BaseLLM(ABC):
    @abstractmethod
    def chat(self, ...): ...
    
class MyLLM(BaseLLM):   # 必须写 (BaseLLM)
    def chat(self, ...): ...

# Protocol：不需要继承，只要"长得像"就行
class ToolCallingLLM(Protocol):
    def chat(self, ...): ...

class MyLLM:            # 不用继承任何东西
    def chat(self, ...): ...
```

## 二、为什么没有方法体

因为 `Protocol` 类**只用来定义"接口契约"**，本身**永远不会被实例化**，也**不会被调用**。它存在的唯一意义是：

1. **给类型检查器（mypy / pyright / IDE）看**：告诉它们"任何有 `chat(messages, tools) -> LLMResponse` 方法的对象，都可以当作 `ToolCallingLLM` 用"
2. **给读代码的人看**：明确这个 Agent 依赖的 LLM 需要满足什么接口

所以方法体写 `...` 就够了，Python 语法上 `...` 是一个合法的表达式语句（`Ellipsis` 对象），放在函数体里可以占位。如果你真的去实例化并调用它，会返回 `None`——但**这个类本来就不该被实例化**。

## 三、在这个文件里的实际作用

回看代码：

```python
class LLMAgent(PaymentAgent):
    def __init__(self, llm: ToolCallingLLM, ...):
        self.llm = llm
```

`llm` 参数的类型标注是 `ToolCallingLLM`，但实际传进来的可以是：
- `OpenAICompatibleLLM`（这个文件里定义的）
- 任何**你自己写的**、只要实现了 `chat(messages, tools) -> LLMResponse` 方法的类
- 测试时用的 **Mock/Fake LLM**（这也是注释里说"单元测试不需要安装 openai"的原因——测试时塞一个假 LLM 即可）

它们都**不需要继承** `ToolCallingLLM`，类型检查器会自动认为它们符合协议。这就是"与模型供应商解耦"的实现方式。

## 四、补充：`...` vs `pass` vs `NotImplementedError`

这三种"空方法体"写法含义不同：

| 写法 | 含义 | 适用场景 |
|------|------|----------|
| `...` | 占位，什么都不做 | **Protocol / 抽象接口声明**（本文件） |
| `pass` | 同上，但语义更弱 | 临时占位 |
| `raise NotImplementedError` | 强制子类必须重写 | 传统 ABC 的 `@abstractmethod`，或基类的"必须实现"方法 |

这里用 `...` 是因为它是**纯接口声明**，不会被调用。如果换成 `raise NotImplementedError`，虽然也能跑，但语义上会让人误以为"这个方法有默认行为需要子类覆盖"，不如 `...` 清晰。

## 五、一个小提醒

`Protocol` 只有在**类型检查阶段**生效，**运行时不强制**。也就是说，你传一个没有 `chat` 方法的对象进去，Python 不会在构造时报错，只有等到 `self.llm.chat(...)` 调用时才会抛 `AttributeError`。如果希望在运行时也校验，可以用 `@runtime_checkable` 装饰器 + `isinstance()` 检查，但通常没必要——静态类型检查 + 明确的接口约定已经足够了。

总结一句话：**没有方法体，是因为 `Protocol` 类只定义"契约"而不提供"实现"，`...` 就是给类型系统和开发者看的接口签名占位符。**


todo: 学习依赖图、拓扑排序的理解
```aiignore
    from typing import List

    def get_ready_steps(self) -> List[Step]:
        step_map = {step.step_id: step for step in self.plan.steps}

        # 1. 只保留 pending 步骤
        pending_steps = [step for step in self.plan.steps if step.status == "pending"]

        # 2. 构建 pending 步骤的依赖图
        in_degree = {step.step_id: 0 for step in pending_steps}
        dependents = {step.step_id: [] for step in pending_steps}

        for step in pending_steps:
            if step.depends_on:
                for dep_id in step.depends_on:
                    dep = step_map.get(dep_id)
                    if dep is None or dep.status != "completed":
                        # 依赖未完成或不存在，当前 pending 步骤暂时不能进入执行序列
                        in_degree[step.step_id] += 1
                    else:
                        # 依赖已完成，相当于对 pending 步骤没有阻塞
                        pass

        # 3. 拓扑排序：收集所有可以按顺序执行的 pending 步骤
        queue = [step_id for step_id, deg in in_degree.items() if deg == 0]
        ready_steps: List[Step] = []

        while queue:
            step_id = queue.pop(0)
            step = step_map[step_id]
            ready_steps.append(step)

            for next_step in pending_steps:
                if next_step.depends_on and step_id in next_step.depends_on:
                    in_degree[next_step.step_id] -= 1
                    if in_degree[next_step.step_id] == 0:
                        queue.append(next_step.step_id)

        return ready_steps

```