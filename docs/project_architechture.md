# 记录最终项目的架构和设计

ai-agent-testing/
│
├── config/
├── datasets/
├── src/
│   ├── exceptions/
│   ├── llm/
│   │     ├── llm.py
│   │     ├── llm_client.py
│   └── utils/
│
├── tests/
│   └── week01/
│
├── reports/
├── docs/
│   ├── learning_progress.md
│   ├── daily_review.md
│   ├── technical_notes.md
│   └── project_architecture.md
├── .env
├── .gitignore
└── requirements.txt

其中：
- learning_progress.md：记录每天学习进度和评分。
- daily_review.md：记录每天发现的缺陷和改进。
- technical_notes.md：沉淀知识点。
- project_architecture.md：记录最终项目的架构和设计。

文件	职责
state.py：	保存 Agent 执行过程中的状态
agent.py：	控制 Agent 的执行流程
order_tool.py：	查询订单
permission_tool.py：验证用户权限
refund_tool.py：	执行退款