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