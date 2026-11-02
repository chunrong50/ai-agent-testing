## 16周课程目录
这是我们的完整课程安排。
阶段 	周次 	课程主题	     最终成果
第一阶段	W1 LLM基础及API测试	大模型测试程序
	W2	Prompt工程与测试	    Prompt测试集
	W3	Agent架构与运行机制	第一个Agent
	W4	RAG、Embedding、MCP	电商知识库Agent
第二阶段	W5 Tool Calling测试	 工具测试模块
	W6	RAG测试	             RAG评估模块
	W7	Memory测试	       多轮对话测试模块
	W8	Workflow与Multi-Agent	售后Agent
第三阶段	W9 Pytest自动化框架	自动化测试框架
	W10	DeepEval与LLM Judge	质量评估模块
	W11	LangSmith与Trace	链路分析模块
	W12	Agent回归与CI/CD	    自动回归体系
第四阶段	W13	Agent安全测试	安全测试模块
	W14	性能与稳定性测试	    性能测试报告
	W15	电商支付Agent完整项目	项目集成
	W16	项目验收与面试	    项目作品集

## 每一天都采用五步教学法：
1. 课程（Learn）
   
   学习当天的技术知识、核心概念、架构原理。
2. 编码（Code）
   
   跟着实战任务写 Python 代码，运行 Agent 或测试工具。
3. 测试（Test）
   
   自己设计测试用例，执行测试，观察异常和缺陷。
4. 分析（Analyze）
   
   分析失败原因，理解模型行为、工具调用及业务逻辑。
5. 复盘（Review）
   
   整理技术笔记、测试报告、代码及当天学习成果。

## 16 周学习连续性管理
1. 每天：学习与代码实战
   课程讲解 → 编码 → 测试 → 提交 → 评审 → 修改。
2. 每 5 天：阶段复盘
   汇总知识点、代码、评分、问题和薄弱项。
3. 每 10 天：建立新聊天
   带上最新学习档案，继续后面的课程。
4. 每 4 周：阶段验收
   检查知识掌握程度、代码能力和阶段项目成果。
5. 第 16 周：最终项目验收
   完成电商支付 AI Agent 测试平台，整理项目文档和面试材料。


## 第一周 每日课程安排
日期	    课程     	        编码任务	         测试任务
Day 1	AI与LLM基础	        建立项目环境	    测试基础问答
Day 2	Transformer、Token	编写Token统计程序	测试超长输入
Day 3	Temperature、随机性	编写模型参数配置	测试输出稳定性
Day 4	Prompt Engineering	编写电商Prompt	测试指令遵循
Day 5	幻觉与模型局限	    编写答案校验程序	测试虚假信息
Day 6	LLM API及结构化输出	Python调用模型	测试JSON输出
Day 7	Pytest自动化及总结	建立测试脚本	    输出第一份测试报告


我的建议是：
学习阶段	聊天安排
Day 1～Day 5	一个聊天
Day 6～Day 10	新开一个聊天
Day 11～Day 15	新开一个聊天
后续	每 5～10 天拆分一个聊天

这样既保留连续性，也降低历史上下文过长的风险。


## 后续上下文容量不够，怎么继续？
我建议建立一个简单的机制：学习档案 + 阶段性总结 + 新聊天接续。
具体分三步。
### 第一步：每 5～10 天生成一次学习档案
学习档案固定记录：
记录项目	内容
总体目标	转型 AI Agent 测试工程师
学习路线	16 周、约 80 个学习日
已完成课程	Day 1、Day 2
每日评分	Day 1：88分；Day 2：89分
技术能力	Python、Pytest、TokenCounter、ContextChecker
已发现问题	类型校验、上下文边界、测试职责划分等
当前进度	Day 2 已通过，下一步 Day 3
项目代码	目录结构、关键代码、测试结果
后续任务	Prompt Engineering 与 Prompt 测试

这样，即使换了聊天窗口，也不会丢失学习进度。
###  第二步：新聊天时，把学习档案交给我
例如新开聊天后，直接发送：
这是我 AI Agent 测试工程师转型学习的阶段性档案。

请延续之前的导师教学模式：
1. 每天有明确的学习目标和知识点。
2. 结合电商支付 Agent 实战。
3. 布置 Python + Pytest 编码任务。
4. 我提交代码和测试结果后，请逐项评审。
5. 给出评分、问题分析和修改建议。
6. 达到验收标准后再进入下一天。

请先阅读学习档案，确认我的学习进度，
从下一个未完成的学习日继续。


### 第三步：保留代码工程，不依赖聊天记录保存代码
你的 ai-agent-testing 本地项目是最重要的资产。

建议持续维护：
ai-agent-testing/
├── src/
├── tests/
├── datasets/
├── reports/
├── docs/
│   ├── learning_progress.md
│   ├── daily_review.md
│   ├── technical_notes.md
│   └── project_architecture.md
└── README.md

其中：
- learning_progress.md：记录每天学习进度和评分。
- daily_review.md：记录每天发现的缺陷和改进。
- technical_notes.md：沉淀知识点。
- project_architecture.md：记录最终项目的架构和设计。
这些文件可以随着学习不断更新。换聊天窗口时，也可以上传最新档案继续学习。