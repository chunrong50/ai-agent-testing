# 大模型多步推理场景

用户："帮我退款订单 123"

第 1 轮：
  LLM 看到用户请求 → 决定调用 query_order(order_id="123")
  Agent 执行，得到 observation: {success: true, data: {...订单信息...}}
  把 observation 追加进 messages

第 2 轮：
  LLM 看到 messages 里有了订单信息 → 决定调用 execute_refund(order_id="123")
  Agent 执行退款，得到结果
  把结果追加进 messages

第 3 轮：
  LLM 看到退款成功 → 没有 tool_calls 了，返回 content: "已为您退款成功"
  Agent 检测到 no tool_calls → 返回最终结果，退出循环