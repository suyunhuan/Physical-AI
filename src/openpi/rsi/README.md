# openpi.rsi — 榜单对齐的轻量长程评测 / 训练钩子

- `subgoal_checklist.py`：Q-score 式子目标完成率
- `wheeled_bimanual_sim.py`：固定 8 任务轮式双臂家庭闭环套件（CPU stub，非 B1K 官方）
- `checklist_policy.py`：checklist 条件策略头 + 数据过滤 + CPU 逻辑回归训练

完整 π0/π0.5 微调仍需 **Linux + CUDA GPU** 与权重；本包同时提供：
- CPU stub 闭环（Mac / 无 GPU）
- 本机环境探测与 openpi/B1K 启动器（见下）

## 入口脚本
| 脚本 | 用途 |
|---|---|
| `scripts/rsi/run_first_idea_loop.py` | CPU checklist idea 闭环 |
| `scripts/rsi/detect_env.py` | 探测 CUDA / Mac / 磁盘 / B1K |
| `scripts/rsi/run_openpi_train.py` | 真实 openpi 短训（需 GPU；`DOWNLOAD_WEIGHTS=1`） |
| `scripts/rsi/run_b1k_aligned_eval.py` | B1K 协议评测或官方钩子 |
| `scripts/rsi/run_local_pipeline.py` | 一键 mode 选择 |

Runbook：`rsi/docs/local-gpu-openpi-b1k.md`  
Train config：`pi0_libero_checklist_smoke`
