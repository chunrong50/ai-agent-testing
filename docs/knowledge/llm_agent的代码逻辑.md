# llm_agent.py 代码逻辑与业务流

## 一、文件结构

| 部分 | 作用 |
|---|---|
| `ToolCall` / `LLMResponse` | 与供应商无关的数据结构，描述“LLM 想调用什么工具”和“LLM 的一次回复” |
| `ToolCallingLLM`（Protocol） | 只规定一个 `chat(messages, tools)` 方法，FakeLLM 和真实模型都实现它 |
| `OpenAICompatibleLLM` | 真实模型适配器，只在 Smoke Test 里用 |
| `LLMAgent` | 核心，继承 Day 4 的 `PaymentAgent` |
| `build_default_agent` | 用 Day 4 的三个 Tool 组装一个可用的 Agent |

## 二、三方职责

```
LLM    ：只"说"要调用哪个工具、传什么参数（返回 tool_calls），不执行任何代码
Agent  ：校验 LLM 的请求 → 执行 Python Tool → 把结果回传给 LLM
Tool   ：真正的业务逻辑（OrderTool / PermissionTool / RefundTool）
```

## 三、主流程：`run()`

```
用户输入 "帮我退款 ORD1001"
   │
   ▼
messages = [system 提示词, user 消息]
   │
   ▼  ┌──────────────── 最多循环 max_steps 次 ────────────────┐
   │  │                                                        │
   │  │  llm.chat(messages, tools=TOOL_SCHEMAS)                │
   │  │        │                                               │
   │  │        ├─ 没有 tool_calls → LLM 给出最终回复 → _finish 结束
   │  │        │                                               │
   │  │        └─ 有 tool_calls：                              │
   │  │             1. 把 assistant 的 tool_calls 追加进 messages│
   │  │             2. 逐个 execute_tool() 执行                │
   │  │             3. 把结果作为 role=tool 消息追加进 messages │
   │  │             4. 回到循环顶部，让 LLM 看到结果再决定下一步│
   │  └────────────────────────────────────────────────────────┘
   ▼
超过 max_steps → 记录错误，status=failed（防死循环）
```

关键点：
- **第二次调用 LLM 时，messages 里已经带着工具的 Observation**，LLM 据此生成“退款成功”之类的最终回复。
- 整个 `run()` 外层有 `try/except`，LLM 接口超时、500 等异常会被兜住，返回“系统执行异常，请稍后重试”，状态为 `failed`。
- 返回的是 `AgentState`，和 Day 4 的 `PaymentAgent.run()` 一致，`trace`、`tool_calls`、`status`、`error` 都能复用。

## 四、安全关卡：`execute_tool()`

LLM 的输出不可信，每个工具调用要依次过四关：

```
① 白名单      工具名必须在 ALLOWED_TOOL_NAMES 里      → 否则 UNKNOWN_TOOL
② JSON 解析   arguments 必须是合法 JSON 对象          → 否则 INVALID_ARGUMENTS
③ Schema 校验 必填项齐全、类型是非空字符串、无多余字段 → 否则 INVALID_ARGUMENTS
               （LLM 自己传 user_id 也会在这里被拒）
④ 执行        调用对应的 Python 方法，异常被捕获      → 否则 TOOL_EXCEPTION
```

- **`user_id` 的来源**：它来自 `run(user_id, ...)` 的会话信息，由 Agent 注入，**从不来自 LLM**。这样 LLM 无法冒充别人。
- **失败不崩溃**：被拒绝的调用会通过 `_reject()` 返回 `{"success": False, "error": 错误码}`，同时写入 `state.error` 和 trace，并作为 Observation 回传给 LLM，让它向用户如实说明。
- 任何工具返回 `success=False`，`state.error` 都会被设置，最终 `status` 为 `failed`。

## 五、两个业务工具

### `query_order`（只读）
```
OrderTool.query_order(order_id)
   ├─ 订单不存在 → 返回错误
   ├─ 订单不属于当前 user_id → 返回错误（不把订单内容给 LLM，防信息泄露）
   └─ 通过 → 写入 state.order_id / state.order_data，返回订单数据
```

### `execute_refund`（敏感操作）
**LLM 选了这个工具，不等于就会退款**，Agent 固定走四步：

```
LLM 选择 execute_refund
        │
  ① 查询订单 + 归属校验      （复用 _tool_query_order）
        │ 失败 → 直接返回，不往下走
  ② PermissionTool.check_permission
        │ 无权限 → 返回"用户无权操作该订单"
  ③ RefundTool.execute_refund
        │ 内部再校验：订单存在、归属、已支付、未重复退款
  ④ 修改订单 refund_status = REFUNDED，返回退款结果
```

这是**纵深防御**：归属在 Agent 层校验一次、PermissionTool 校验一次、RefundTool 内部又校验一次，任何一层失败都不会退款。

## 六、一个完整例子

用户 U001 说：“帮我退款 ORD1001”

1. **第 1 轮**：LLM 返回 `execute_refund(order_id="ORD1001")`
2. Agent 过四道关，进入 `_tool_execute_refund`
3. 依次调用 `query_order`、`check_permission`、`execute_refund`，`state.tool_calls` 里留下这三条记录
4. 结果 `{"success": True, "refund_amount": 199.0, ...}` 以 role=tool 回传
5. **第 2 轮**：LLM 看到成功结果，返回文本“退款成功，金额 199 元”（没有 tool_calls）
6. `_finish(state, 回复文本, "success")`，流程结束

## 七、和 Day 4 的对比

| | Day 4 `PaymentAgent` | Day 5 `LLMAgent` |
|---|---|---|
| 决定调用哪个工具 | Python 关键词规则 | LLM |
| 订单号提取 | 正则 | LLM 生成参数 |
| 最终回复 | Python 拼接固定话术 | LLM 生成 |
| 权限、业务规则校验 | Python | **同样是 Python，不变** |
| 返回值 | `AgentState` | `AgentState` |

一句话总结：**LLM 只负责“理解意图 + 选工具 + 生成参数”，所有校验和执行仍然由确定性的 Python 代码完成。** 这也是面试时最该强调的设计原则：不要信任 LLM 的输出，安全边界必须放在后端。