# Automation 名称：RSI-每日论文日报
# Trigger：Scheduled，cron = 0 7 * * *（每天 07:00）
# Repository：Single repository = suyunhuan/Physical-AI
# Tools：Memories；不启用 Slack / PR Comment
# Model：Gemini 最新 Pro 长上下文档
# 状态：增量更新（榜单冲顶强相关）；控制台需同步替换 Prompt

先读取 rsi/paper-log.md、rsi/keywords.md、rsi/leaderboard.md；paper-log 是去重唯一硬依据，Memory 仅用于加速识别。
检索近 7 天 arXiv cs.RO/cs.AI/cs.CV/cs.LG 与公开论文源：开放技术路线 + 榜单冲顶相关（B1K、家庭长程、数据效率、跨形态、轮式双臂）。
选择 3 篇前沿 Top + 1-2 篇短期强相关；强相关优先能推进主榜 Q-score / 数据×形态联合者。
候选必须标注技术路线，优先补检最近 7 次运行覆盖不足的路线；如果当天候选全是 VLA，补检 TAMP、世界模型/MPC、RL/自改进、仿真数据、感知记忆或安全评测方向。只收录合格工作，不为满足路线配额降低证据或相关性标准。
逐篇输出 idea 卡片（字段遵循 rsi-core，必须含技术路线；不得在研读阶段因无法直接映射 openpi 而排除论文），写入 rsi/daily/YYYY-MM-DD.md。
把本次推送追加到 rsi/paper-log.md，并在同一分支提交 rsi/daily 与 rsi/paper-log.md；不拉权重、不开训。
若当天没有合格强相关论文，允许只推 3 篇前沿 Top，并在日报中说明原因；不得为凑数编造论文。
