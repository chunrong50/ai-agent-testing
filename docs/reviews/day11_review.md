## 最后一道理解题
假设：
- Memory 中记录订单 A10086 已支付。
- 用户再次发起退款请求。
- 订单系统查询发现订单已经退款。
问题：为什么 Agent 不能直接使用 Memory 中的订单状态决定是否退款？Memory 在这个过程中应该发挥什么作用？
一、理解题评审
你的回答：
因为 memory 中的订单状态可能存在滞后性，实际结果应该以业务系统的结果为准，比如订单信息、退款状态这些都应该以业务系统的实际结果为准。Memory 在过程中发挥的是参考作用，并不作为决定作用。

回答正确
你抓住了三个关键点：
1. 数据可能滞后：Memory 可能保存旧信息。
2. 数据来源优先级：订单状态、退款状态等以业务系统实时查询结果为准。
3. Memory 的定位：提供上下文和参考信息，而不是业务决策的最终依据。
我再帮你补充一个面试中更完整的表达：

Agent Memory 主要用于保存历史上下文和用户偏好，帮助 Agent 理解当前请求。但 Memory 不保证业务数据的实时性和准确性，因此涉及支付、退款、订单状态和权限等关键业务决策时，必须调用对应的业务工具获取最新数据，并以业务系统返回结果为准。

这段可以作为你的面试答案。

如果 Memory 读取失败，但订单查询工具和权限校验工具都正常，Agent 是否可以继续执行退款流程？为什么？
面试级回答优化
你可以这样回答：
Memory 读取失败不一定意味着 Agent 必须终止整个任务。Agent 可以继续执行订单查询和权限校验等非破坏性操作。
但是，是否允许退款必须依据业务系统的实时数据和退款工具内部的业务校验结果来决定，不能依赖 Memory 中的历史记录，也不能因为 Memory 读取失败而跳过必要的业务校验。
如果退款所需的关键业务条件无法确认，Agent 应该停止退款操作并向用户返回明确的错误信息。
这个版本已经比较符合初级 AI Agent 测试工程师的面试要求。


问题 1：get_ready_steps()
当 Plan 中：
- Step 1：completed
- Step 2：completed
- Step 3：failed
- Step 4：pending，依赖 Step 3
Agent 再次获取 ready steps 时，应该如何处理？

需要理解：
- failed 的 Step 是否可以执行？
- 依赖 failed Step 的任务是否可以执行？
- 什么情况下可以继续执行后续任务？
一、问题一：Step 失败之后的执行机制
你回答的核心是：
- Step 3 failed，Engine 进入结束流程。
- 不依赖 Step 3 的 pending Step 可以继续执行。
这里有一个关键问题：你把 get_ready_steps() 的调度能力和 Engine 的执行控制混在了一起。

需要区分两个层面：
第一层：get_ready_steps()
假设：
Step	状态	依赖
Step 1	completed	无
Step 2	completed	无
Step 3	failed	Step 1
Step 4	pending	Step 3
Step 5	pending	Step 2

单看调度逻辑：
- Step 4 不应该执行，因为依赖的 Step 3 没有成功完成。
- Step 5 的依赖已经满足，因此可以被识别为 ready。
第二层：Engine 执行控制

但是，根据我们之前讨论的 LLMPlanAgent 实现，工具执行失败后会：
1. 保存 Step 执行结果。
2. 记录 Observation。
3. 将 Step 和 Plan 标记为 failed。
4. 调用 _finish(..., "failed")。
5. 结束当前 Engine 执行。
因此，即使 Step 5 满足依赖条件，当前 Engine 也不会继续执行它。

这就是你这道题需要修正的地方。