# Automation 名称：RSI-关键词雷达
# Trigger：Scheduled，cron = 30 6 * * *（每天 06:30，先于论文日报）
# Repository：Single repository = suyunhuan/Physical-AI
# Tools：Memories、MCP（如需外部数据源）；不启用 PR 评论/Slack
# Model：Gemini 最新 Pro 长上下文档
# 状态：增量更新（榜单冲顶 / 数据×形态）；控制台需同步替换 Prompt

读取 .cursor/rules/rsi-core.mdc、rsi/keywords.md 与 rsi/paper-log.md、rsi/leaderboard.md。
按社区热度、机器人公司/大厂、创业公司、高校实验室、中文社区 5 路检索近 7 天信号，并按 R1–R8 与 R9（榜单/数据×形态）归类。
额外必扫：BEHAVIOR-1K/BEHAVIOR Challenge、RoboCasa 榜、家庭长程挑战赛、数据引擎、跨形态、轮式双臂/移动操作。
输出 rsi/daily/YYYY-MM-DD-radar.md，并更新 rsi/keywords.md：新增关键词必须附日期、来源、相关性和技术路线；降权必须保留历史理由。
必须检查路线覆盖矩阵；若 VLA 以外路线与榜单信号没有结果，明确标注“未覆盖”并补检，不得用 VLA 结果凑满 Top 5。
将“本次关键词变更摘要”写入 Automation Memory；只提交 rsi/daily 与 rsi/keywords.md 的变更，不修改代码、不拉权重、不开训。
若检索源不可用，标注“未覆盖”，不得编造来源。
