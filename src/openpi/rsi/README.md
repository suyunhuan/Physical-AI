# openpi.rsi — 榜单对齐的轻量长程评测 / 训练钩子

- `subgoal_checklist.py`：Q-score 式子目标完成率
- `wheeled_bimanual_sim.py`：固定 8 任务轮式双臂家庭闭环套件（CPU stub，非 B1K 官方）
- `checklist_policy.py`：checklist 条件策略头 + 数据过滤 + CPU 逻辑回归训练

完整 π0/π0.5 微调仍需 GPU 与权重；本包用于 RSI 第一版可测闭环。

入口脚本：`scripts/rsi/run_first_idea_loop.py`
