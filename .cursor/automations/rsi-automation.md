# Automation 名称：RSI-自迭代调度
# Trigger：Scheduled，cron = 0 18 * * 5（每周五 18:00）
# Repository：Single repository = suyunhuan/Physical-AI
# Tools：Memories、MCP（可选）；允许创建 PR
# Model：Claude Opus 最新高推理档；预算内轻量步骤可交给 Auto/Composer
# 状态：草稿 — 需用户确认登录、关联仓库、预算后再激活；禁止自动启用

读取 rsi/experiments/experiment-tree.md、rsi/reports 与 rsi/plans，生成本周 RSI 复盘：
有效改动、失败假设、指标变化、下一轮预算建议。只允许提出最多 3 个下一步候选，按预期收益/成本/风险排序。
若候选可自动验证，创建独立分支执行最小实验；否则只输出 rsi/experiments/YYYY-MM-DD-rsi-report.md 并等待人工批准。
预算用尽即停；禁止无预算限制地持续改代码。
