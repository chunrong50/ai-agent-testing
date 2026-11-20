今天正式进入 **Day 21：AI Agent 自动化测试框架设计与实战**。

从今天开始进入第二阶段：项目实战能力。

第一阶段 Day 1–20 的重点是理解 Agent 的架构、执行机制、Memory、Planning、Trace、可靠性以及 LLM Evaluation。

第二阶段不再大量重复测试场景，而是把前面学过的知识整合起来，逐步建立一套可以用于真实 AI Agent 项目的自动化测试框架。

# **Day 21：Pytest 自动化测试框架设计**

第二阶段

Day 21 / 40

项目实战

## **一、今天的学习目标**

今天重点解决一个问题：

**如果一个项目中有几十个 Agent、上百个 Tool，应该如何设计一套可复用的自动化测试框架？**

我们不再为每个测试用例重复创建 Agent、FakeLLM、Mock Tool，而是建立统一的测试基础设施。

今天只学习四个知识点：

| 知识点             | 学习目标             |
| --------------- | ---------------- |
| Pytest Fixtures | 统一管理测试环境         |
| FakeLLM         | 模拟 LLM 响应，控制测试过程 |
| Mock Tool       | 模拟工具执行及返回结果      |
| 测试数据管理          | 减少重复代码，提高用例复用性   |

## **二、先理解真实项目中的测试框架**

假设我们现在有一个电商退款 Agent：

## **AI Agent 自动化测试框架**

**Test Cases**

测试业务场景、执行流程、异常行为

**Pytest 测试管理层**

**Fixtures**

测试环境初始化

**Parametrize**

参数化测试

**FakeLLM**

模拟模型响应

**Mock Tool**

模拟工具执行

**Agent 被测系统**

LLMPlanAgent / AgentState / ToolExecutor / Memory

**Assertions & Test Reports**

验证结果、执行次数、调用记录、测试报告

这里需要理解一个核心思想：

**测试用例只负责描述测试目标，测试框架负责提供统一的测试环境。**

例如：

今天测试正常退款，明天测试无权限退款，后天测试退款金额异常。

这三个测试不应该每次都重新创建 FakeLLM、Agent 和 Tool。

这些公共对象应该由 Fixtures 统一提供。

## **三、知识点 1：Pytest Fixtures**

Fixtures 是今天最重要的知识点。

先看两种写法。

**写法 A：每个测试独立创建环境**

```
def test_normal_refund():    llm = FakeLLM(...)    agent = LLMPlanAgent(llm=llm)    tool = RefundTool()    # 执行测试def test_refund_without_permission():    llm = FakeLLM(...)    agent = LLMPlanAgent(llm=llm)    tool = RefundTool()    # 执行测试
```

问题：

- 重复创建测试环境。
- 修改 Agent 初始化方式时，需要修改多个测试。
- 测试代码越来越臃肿。

**写法 B：使用 Fixtures**

在 `tests/conftest.py` 中统一创建：

```
import pytest@pytest.fixturedef env():    llm = FakeLLM()    agent = LLMPlanAgent(llm=llm)    return {        "llm": llm,        "agent": agent    }
```

测试用例直接使用：

```
def test_normal_refund(env):    agent = env["agent"]    llm = env["llm"]    # 执行测试
```

这样每个测试用例就不需要重复创建公共测试对象。

### **需要掌握的两个概念**

| 概念      | 含义               |
| ------- | ---------------- |
| Fixture | 提供测试所需的对象和环境     |
| Scope   | 控制 Fixture 的生命周期 |

常见 Scope：

- `function`：每个测试函数创建一次。
- `class`：每个测试类创建一次。
- `module`：每个测试文件创建一次。
- `session`：整个测试会话创建一次。

对于 Agent 测试，需要特别注意：

**AgentState、Memory 等具有状态的对象，通常应该使用 function 级别，避免不同测试用例之间互相污染。**

## **四、今天的代码实践**

今天先不要求你重新编写整个 Agent。

我们以你现有的 `ai-agent-testing` 项目为基础，重点改造测试框架。

建议结构：

```
ai-agent-testing/
│
├── src/
│   ├── agent/
│   └── tools/
│
├── tests/
│   ├── conftest.py
│   │
│   ├── fixtures/
│   │   └── test_data.py
│   │
│   └── week03/
│       └── test_framework.py
│
└── pytest.ini
```

### **Day 21-01：第一个练习**

今天先完成 Fixtures 的设计，不急着写复杂代码。

请根据下面三个问题回答。

**Day 21-01 知识检查**

0/3 已回答

**1. 为什么应该把 Agent、FakeLLM 等公共测试对象放在 conftest.py 中，而不是每个测试用例中重复创建？**

为了让所有测试用例共享同一个 Agent 实例

为了统一管理测试环境，减少重复初始化代码

为了让测试执行速度一定更快

**2. 两个测试用例分别需要独立的 AgentState 和 Memory，应该优先使用什么 Scope？**

session

module

function

**3. 如果测试 A 修改了 Memory 中的 user_id，测试 B 不应该受到影响，应该如何设计？**

两个测试共享同一个 Memory

每个测试初始化独立的 Memory

使用 session 级别的 Memory

提交答案

## **五、Day 21 验收标准**

今天不追求写很多代码，重点是理解测试框架的设计思想。

- 理解 Fixture 的作用。
- 理解不同 Scope 的区别。
- 能够使用 Fixture 创建 Agent 测试环境。
- 理解为什么 Memory、AgentState 需要隔离。

**后续安排：**

| 学习日      | 主要内容                     |
| -------- | ------------------------ |
| Day 21   | Pytest Fixtures 与测试环境设计  |
| Day 22   | FakeLLM、Mock Tool 与参数化测试 |
| Day 23   | 测试数据管理与公共测试基类            |
| Day 24 起 | Agent 综合项目测试与评估          |

我会继续按照之前的导师式学习方式：你先回答、提交代码和 pytest 结果，我再逐项评审、评分，通过验收后进入下一节。

**今天先完成 Day 21-01，不要急着写完整测试框架。**

对，你说得对。Day 21 不应该再让你从零学习和编写 conftest.py。

你之前的项目已经有统一的测试环境设计，而且我们之前的 Day 4–Day 20 也一直在使用这套测试基础设施。

如果继续讲解如何创建 FakeLLM、Agent、Memory 等公共对象，就会变成重复学习。

我们应该调整 Day 21 的学习重点：

不是重新学习 Pytest Fixtures，而是评估现有测试框架是否满足真实 AI Agent 项目的自动化测试需求，并在现有基础上补齐能力。

我已经检查了你 GitHub main 分支当前的 tests/conftest.py。这次以仓库实际代码为准。查看 conftest.py
一、你已经实现的内容
现有实现	评估
FakeLLM	已实现
FakeJudge	已实现
TimeoutOrderTool	已实现
TimeoutRetryOrderTool	已实现
env Fixture	已实现
env_timeout_order_tool	已实现


说明你已经掌握了基础的测试环境管理、Fake 对象和异常工具模拟。
二、现有框架还值得改进的地方
我发现三个值得进一步研究的问题：

1. 测试环境还没有完全统一

当前 env 主要负责创建三个 Tool，并没有统一提供 FakeLLM 和 Agent。

这意味着不同测试文件可能还需要自己初始化 Agent 和 FakeLLM。

2. Fixture 存在一定重复

例如：
- env_timeout_order_tool
- env
三个 Fixture 都重复创建 PermissionTool、RefundTool 和 tools 字典。

后续可以研究如何通过 Fixture 组合减少重复。

3. 测试环境与测试场景的边界

例如 TimeoutOrderTool 是一种特殊测试工具，它应该作为测试基础设施存在，而不是混入正常业务 Tool。

需要理解如何管理不同类型的测试替身。

三、重新确定 Day 21 的学习内容
调整后的学习方向
今天不再学习 Fixture 基础知识，而是学习：

Day 21：AI Agent 自动化测试框架的设计与优化

今天的核心任务是：
1. 分析现有 conftest.py 的设计。
2. 理解 Fixture 组合与依赖注入。
3. 研究如何统一 Agent、FakeLLM、Tools 的初始化。
4. 理解正常测试环境与异常测试环境的管理方式。
不要求今天全部重构，也不为了增加代码量而增加测试用例。
Day 21-01：先回答一个实际问题
你目前的 env：
@pytest.fixturedef env():    
order_tool = OrderTool()   
permission_tool = PermissionTool()    
refund_tool = RefundTool(order_tool.orders)    tools = {        "query_order": order_tool,        "permission_check": permission_tool,        "execute_refund": refund_tool    }    return {        "tools": tools,        "orders": order_tool.orders    }



假设未来有 50 个 Agent 测试用例，每个测试都需要：
- FakeLLM
- LLMPlanAgent
- 三个业务 Tool
- AgentState
你认为应该如何设计 Fixture，才能让测试用例只需要关注测试场景，而不需要重复初始化这些对象？

先说你的设计思路，不用写代码。

我会根据你的回答继续讲解，而不是再让你重复已经掌握的内容。