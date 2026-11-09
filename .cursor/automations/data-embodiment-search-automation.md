# Automation 名称：RSI-数据形态联合搜索
# Trigger：Scheduled，cron = 0 16 * * 3（每周三 16:00）
# Repository：Single repository = suyunhuan/Physical-AI
# Tools：Memories；可选 MCP；允许创建 PR
# Model：Gemini 最新 Pro 长上下文档（权衡过重时可改 Opus 5 High）
# 状态：仓库草稿 — 控制台需粘贴创建；Enabled 默认 false

你做「数据 × 形态」联合搜索，服务 B1K 冲顶与轮式双臂家庭闭环仿真。
读取 rsi-core、rsi/leaderboard.md、rsi/leaderboards/log.md、rsi/keywords.md、rsi/experiments/experiment-tree.md。
硬约束：不得先锁死单一形态再凑数据；每个候选必须是四元组 H=(任务切片, 形态配置, 数据配方, 评测口径)。
步骤：
1. 基于榜差距与失败模式，提出恰好 3 个 H 候选：至少一个以数据配方为主杠杆，至少一个以轮式双臂形态/控制接口为主杠杆，第三个可混合。
2. 每个候选写清：预期影响的主指标（Q-score / 全任务成功率）、数据来源与过滤、形态假设、与 openpi 或外部仿真的映射、成本、风险、回退。
3. 写入 rsi/plans/YYYY-MM-DD-data-embodiment.md，并在 rsi/leaderboards/log.md 追加候选索引。
4. 不要下载数据集或权重、不要开训；只产出可执行的下一轮实验设计。
5. 仅提交 rsi/plans 与 rsi/leaderboards（及必要的 keywords 增补）。
