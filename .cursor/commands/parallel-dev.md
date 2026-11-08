把以下特性方案拆成可并行的开发任务并在隔离工作树中执行（RSI pipeline C5）。

特性方案：<粘贴 rsi/plans 中的方案>

步骤：
1. 任务拆解：拆成低耦合子任务（如：数据转换改造 / 模型改动 / 训练配置 / 评测脚本），列出依赖关系。
2. 为每个子任务创建 git worktree（git worktree add ../<repo>-wt-<task> <branch>），
   每个工作树对应一个独立 Cursor 窗口或 Agents Window 中的独立 Agent，禁止跨工作树覆盖文件。
3. 每个 Agent 完成自己的改动并跑最小冒烟验证（import 检查 / 单步数据加载 / 短步数训练 dry-run）。
4. 汇总每个候选的 diff 与自测结果；若方案要求多候选对比，让不同工作树各实现一个候选。
5. 输出交接清单写入 rsi/experiments/YYYY-MM-DD-handoff.md：
   每个候选的工作树路径 / 改动摘要 / 自测结果 / 建议评测口径，供 C6 使用。

约束：worktree 隔离是硬要求；未通过自测的改动不得进入交接清单。
