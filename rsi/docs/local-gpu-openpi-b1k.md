# 本机运行：openpi 训练 + B1K 对齐评测

面向：**Linux + NVIDIA CUDA** 跑真实 openpi；**Mac Mini** 跑检测 / CPU stub / 协议评测。

## 0. 一键探测

```bash
cd /path/to/Physical-AI
python3 scripts/rsi/detect_env.py
# 或
python3 scripts/rsi/run_local_pipeline.py --mode dry-run
```

| 平台 | 推荐 mode |
|---|---|
| macOS Apple Silicon | `mac`（MLX/MPS）/ `all-safe` / `b1k-protocol` |
| macOS Intel | `cpu-stub` / `all-safe` / `b1k-protocol` |
| Linux + CUDA GPU | `openpi-gpu` + 日后 `b1k-official` |
| 本 Cloud VM（无 GPU） | `cpu-stub` / protocol |

Apple Silicon 专用 runbook：`rsi/docs/mac-silicon-ops.md`。

## 1. Mac Mini 能做什么 / 不能做什么

**可以**
- `detect_env` / `dry-run`（含 MLX/MPS/内存）
- **`--mode mac`**：checklist 头用 MLX（优先）或 PyTorch MPS 短训 + 协议评测
- 第一版 idea CPU 闭环：`run_first_idea_loop.py`
- B1K **协议**评测（轮式双臂固定套件 + Q-score，非官方榜）

**不可以（官方 openpi 路径）**
- π0/π0.5 JAX GPU 微调与 LIBERO/B1K 真仿真（需 Linux+CUDA；Mac 无 NVIDIA）

## 2. Linux + CUDA：真实 openpi 短训（第一 idea 配置）

### 2.1 依赖
```bash
git submodule update --init --recursive
# 按仓库 README 安装 uv，然后：
GIT_LFS_SKIP_SMUDGE=1 uv sync
GIT_LFS_SKIP_SMUDGE=1 uv pip install -e .
```

### 2.2 权重下载开关（默认不拉）
大权重不会自动下载。需要时：

```bash
export DOWNLOAD_WEIGHTS=1
# 可选：export OPENPI_DATA_HOME=/data/openpi-cache
# 建议可用磁盘 ≥40GiB
```

若缓存已有 `~/.cache/openpi/openpi-assets/checkpoints/pi0_base/params`，可不设 `DOWNLOAD_WEIGHTS`。

### 2.3 启动训练
```bash
python3 scripts/rsi/run_openpi_train.py --config pi0_libero_checklist_smoke
# 等价于：
# DOWNLOAD_WEIGHTS=1 uv run scripts/train.py pi0_libero_checklist_smoke --exp-name=rsi_checklist_smoke
```

配置说明（`src/openpi/training/config.py`）：
- 名称：`pi0_libero_checklist_smoke`
- LoRA 微调 `pi0_base`，`num_train_steps=200`，`batch_size=8`
- 数据：`physical-intelligence/libero`（首次会按 LeRobot 流程取数）

无 GPU 时脚本会 **非 0 退出** 并打印中文错误（除非 `ALLOW_CPU_JAX=1`）。

### 2.4 LIBERO 回归评测（openpi 官方路径）
训练出 checkpoint 后，按 `examples/libero/README.md` 起 policy server + client。  
报告时必须标注：**LIBERO = 回归闸门，不是 B1K 榜分数**。

## 3. B1K / 轮式双臂家庭评测

### 3.1 协议干跑（任何机器）
```bash
python3 scripts/rsi/run_b1k_aligned_eval.py --protocol
# 或
python3 scripts/rsi/run_local_pipeline.py --mode b1k-protocol
```

### 3.2 官方 B1K（需自备仿真栈）
1. 按 https://behavior.stanford.edu/challenge/ 安装 BEHAVIOR / OmniGibson  
2. `export B1K_ROOT=/path/to/behavior`  
3. `python3 scripts/rsi/run_b1k_aligned_eval.py --official`  
当前 adapter 会探测安装；若官方 entrypoint 路径因版本而异，在 `src/openpi/rsi/b1k_adapter.py` 中替换 `official_eval_cmd`。

评测口径对齐 RSI：同时报 **端到端成功率** 与 **Q-score / subgoal 完成率**；形态默认 **轮式双臂家庭**。

## 4. 推荐流水线

```bash
# Mac 或无 GPU Linux
python3 scripts/rsi/run_local_pipeline.py --mode all-safe

# CUDA Linux 真训
DOWNLOAD_WEIGHTS=1 python3 scripts/rsi/run_local_pipeline.py --mode openpi-gpu
```

## 5. 与 PR #9 的关系
PR #9 交付 CPU stub 闭环与指标；本 runbook / 脚本把 **同一 idea** 接到可本机执行的 openpi 训练入口与 B1K 协议/官方评测钩子。无真机部署。
