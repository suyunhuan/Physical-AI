# Automation 名称：RSI-关键词雷达
# Trigger：Scheduled，cron = 30 6 * * *（每天 06:30，先于论文日报）
# Repository：Single repository = suyunhuan/Physical-AI
# Tools：Memories、MCP（如需外部数据源）；不启用 PR 评论/Slack
# Model：Gemini 最新 Pro 长上下文档
# 状态：草稿 — 需用户确认登录、关联仓库、预算后再激活；禁止自动启用

读取 .cursor/rules/rsi-core.mdc、rsi/keywords.md 与 rsi/paper-log.md。
按社区热度、机器人公司/大厂、创业公司、高校实验室、中文社区 5 路检索近 7 天信号，并按 8 类开放技术路线归类。
输出 rsi/daily/YYYY-MM-DD-radar.md，并更新 rsi/keywords.md：新增关键词必须附日期、来源、相关性和技术路线；降权必须保留历史理由。
必须检查路线覆盖矩阵；若 VLA 以外路线没有信号，明确标注“未覆盖”并补检，不得用 VLA 结果凑满 Top 5。
将“本次关键词变更摘要”写入 Automation Memory；只提交 rsi/daily 与 rsi/keywords.md 的变更，不修改代码。
若检索源不可用，标注“未覆盖”，不得编造来源。
