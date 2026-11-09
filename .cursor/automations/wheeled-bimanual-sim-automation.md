# Automation 名称：RSI-轮式双臂仿真闭环
# Trigger：Manual 或 Webhook（传入：批准的 H 摘要、任务切片、是否允许训练=默认 false）
# Repository：Single repository = suyunhuan/Physical-AI
# Tools：Memories；可选 MCP；允许创建 PR
# Model：Claude Opus 最新高推理档（Opus 5 High；勿用 medium）
# 状态：仓库草稿 — 控制台需粘贴创建；Enabled 默认 false

对输入的数据×形态假设 H 执行「轮式双臂家庭」最小闭环协议（默认 dry-run / 文档与脚本级）。
默认禁止：下载模型权重、GPU 训练、真机部署。仅当输入明确写「允许训练/允许拉权重」时才可触及，且仍需最小规模。
步骤：
1. 读取 rsi/leaderboard.md 与批准的 plan；确认形态=轮式底盘+双臂，场景=家庭长程，主指标含 Q-score 或等价 BDDL 部分学分 + 端到端成功率。
2. planner：列出仿真入口（B1K/OmniGibson 或卫星栈）、数据配方、评测命令草案、与 openpi 的接口缝隙。
3. 若不可跑仿真：输出阻塞清单与下一步人工项，仍须写报告，不得假装跑过。
4. 若可干跑：只做环境探测/配置校验/小规模脚本 dry-run，不拉大权重。
5. 报告 rsi/reports/YYYY-MM-DD-wheeled-bimanual-<slug>.md；四元组写入 rsi/experiments/experiment-tree.md 与 rsi/leaderboards/log.md。
6. 独立分支开 PR；verifier 未通过不得标 ready。
