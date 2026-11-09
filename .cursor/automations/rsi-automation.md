# Automation 名称：RSI-自迭代调度
# Trigger：Scheduled，cron = 0 18 * * 5（每周五 18:00）
# Repository：Single repository = suyunhuan/Physical-AI
# Tools：Memories、MCP（可选）；允许创建 PR
# Model：Claude Opus 最新高推理档（High）；预算内轻量步骤可交给 Auto/Composer
# 状态：增量更新（榜差距 / H 候选）；控制台需同步替换 Prompt

读取 rsi/experiments/experiment-tree.md、rsi/reports、rsi/plans 与 rsi/leaderboards/log.md，生成本周 RSI 复盘：
与 B1K/#1 的差距、有效 H、失败假设、指标变化、数据杠杆 vs 形态杠杆的收益、下一轮预算建议。
只允许提出最多 3 个下一步 H 候选，按预期收益/成本/风险排序。
若候选可自动验证且未禁止训练/拉权重，创建独立分支执行最小实验；否则只输出 rsi/experiments/YYYY-MM-DD-rsi-report.md 并等待人工批准。
默认不下载权重、不开大规模训练；预算用尽即停；禁止无预算限制地持续改代码。
