# 记录每天学习进度和评分




# AI Agent 测试学习进度

| Day | 主题 | 状态 | 评分 | 源码 | 测试目录 | 补充说明 | 
|---|---|---|---|---|---|---|
| Day1 | 模型输入与 Token | 已通过 | 88 |  src/llm/llm.py,llm_client.py | tests/week01/test_llm_client.py | -|
| Day2 | Context Window | 已通过 | 89 |src/utils/token_counter.py,context_checker.py |  tests/week01/test_context_checker.py、test_token_counter.py | - |
| Day3 | Prompt Engineering 与 Prompt 测试 | 已通过  | 80 | datasets/day03_prompt_cases.json,prompts/payment_agent_system.txt|tests/week01/test_prompt_rules.py||
| Day4 | Agent 架构与运行机制 | 已通过  | 80 |src/agent/agent.py |tests/week01/test_agent_execution.py |补充了LangChain的视频学习课程调整了学习计划，第一阶段以面试为主的学习，第二阶段深入学习 |
| Day5 | Tool calling  |已通过 | 90 |src/agent/llm_agent.py,state.py|tests/week01/test_tool_calling.py| 补充了Python高级用法,参考langchain-course 项目、llm_agent.py代码走读 |
| Day6 |Tool Calling 自动化测试  | 已通过| 88 |src/agent/llm_agent.py |tests/week01/test_agent_reliability.py|补充了Python高级用法,参考langchain-course 项目 |
| Day7 | Agent 架构与执行链路 | 已通过|87  |src/agent/llm_agent.py,state.py |tests/week01/test_agent_loop.py | |
| Day8 | Agent planning与Decision | 已通过| 95|src/agent/planning.py,plan_manager.py |tests/week02/test_plan_manager.py | |
| Day9 | Agent Executor与Plan 执行控制| | || | |
| Day10 | | | || | |
| Day11 | | | || | |

