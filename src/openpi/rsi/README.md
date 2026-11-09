# openpi.rsi — 榜单对齐的轻量长程评测 / 训练钩子

- `subgoal_checklist.py`：Q-score 式子目标完成率
- `wheeled_bimanual_sim.py`：固定 8 任务轮式双臂家庭闭环套件（CPU stub，非 B1K 官方）
- `checklist_policy.py`：checklist 条件策略头 + 数据过滤 + CPU / **MLX / MPS** 逻辑回归训练
- `mac_backend.py`：Apple Silicon 后端探测（MLX > MPS > CPU）与 CUDA 差距说明
- `env_detect.py`：CUDA / Mac Silicon / 内存 / B1K 探测

完整 π0/π0.5 微调仍需 **Linux + CUDA GPU** 与权重；本包同时提供：
- CPU stub 闭环（任意机器）
- **Apple Silicon `mac` 路径**：checklist 头用 MLX/MPS 训，评测协议与 CPU stub 对齐
- 本机环境探测与 openpi/B1K 启动器（见下）

## 入口脚本
| 脚本 | 用途 |
|---|---|
| `scripts/rsi/run_first_idea_loop.py` | CPU checklist idea 闭环 |
| `scripts/rsi/run_mac_train.py` | Mac Silicon MLX/MPS checklist 短训 + 协议评测 |
| `scripts/rsi/detect_env.py` | 探测 CUDA / Mac backend / 磁盘 / B1K |
| `scripts/rsi/run_openpi_train.py` | 真实 openpi 短训（需 CUDA；`DOWNLOAD_WEIGHTS=1`） |
| `scripts/rsi/run_b1k_aligned_eval.py` | B1K 协议评测或官方钩子 |
| `scripts/rsi/run_local_pipeline.py` | 一键 mode（含 `--mode mac`） |

Runbook：`rsi/docs/local-gpu-openpi-b1k.md` · Mac：`rsi/docs/mac-silicon-ops.md`  
Train config：`pi0_libero_checklist_smoke`（CUDA only）
