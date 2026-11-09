# Automation 名称：RSI-单点Idea闭环
# Trigger：Manual 或 Webhook（传入 idea、目标指标、资源约束、可选 H 四元组）
# Repository：Single repository = suyunhuan/Physical-AI
# Tools：Memories、MCP（实验平台/日志，可选）；允许创建 PR
# Model：Claude Opus 最新高推理档（High）
# 状态：增量更新（H 四元组 + 默认禁训）；控制台需同步替换 Prompt

对输入 idea 执行最小验证闭环。输入必须能映射到 H=(任务切片, 形态配置, 数据配方, 评测口径)；缺则先补全再动手。
默认禁止下载权重、GPU 训练、真机；仅当输入明确授权才可小规模训练。
主指标优先 B1K Q-score/全任务成功率或声明的卫星榜；同时报端到端与 subgoal；LIBERO 只可作回归附注。
流程：读结构基线 → 最小可回退改动 →（授权下）小规模实验 → 固定口径评测 → 报告。
先调用 planner subagent 输出计划；实现后调用 verifier subagent 独立验收。
报告写入 rsi/reports/YYYY-MM-DD-<idea-slug>.md，实验四元组写入 rsi/experiments/experiment-tree.md 与 rsi/leaderboards/log.md。
所有改动进入独立分支并开 PR；verifier 未通过时禁止标记 ready for review。
