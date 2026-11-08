# Automation 名称：RSI-单点Idea闭环
# Trigger：Manual 或 Webhook（传入 idea、目标指标、资源约束）
# Repository：Single repository = suyunhuan/Physical-AI
# Tools：Memories、MCP（实验平台/日志，可选）；允许创建 PR
# Model：Claude Opus 最新高推理档
# 状态：仓库草稿已落盘；用户已授权激活，但 cursor.com 控制台对象尚未创建（登录阻塞）— 创建并手动 Run 通过后可 Enable

对输入 idea 执行最小验证闭环：读结构基线 → 最小可回退改动 → 小规模训练/仿真 → 固定口径评测 → 报告。
先调用 planner subagent 输出计划；实现后调用 verifier subagent 独立验收。
报告写入 rsi/reports/YYYY-MM-DD-<idea-slug>.md，实验四元组写入 rsi/experiments/experiment-tree.md。
所有改动进入独立分支并开 PR；verifier 未通过时禁止标记 ready for review。
