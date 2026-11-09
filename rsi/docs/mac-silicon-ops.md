# Apple Silicon（Mac Mini M-series）算子路径

面向 **本机 Apple Silicon**：跑 first-idea checklist + 门控恢复的 **可训练/可评测** 路径；**不是**官方 openpi π0 JAX+CUDA 全量训练。

## 探测

```bash
# 建议用 .venv-mac（见下）或已装 mlx/torch 的 Python
python3 scripts/rsi/detect_env.py
python3 scripts/rsi/run_local_pipeline.py --mode dry-run
```

`detect_env` 会报告：`apple_silicon`、`memory_gb`、`mlx_available`、`mps_available`、`metal_available`、`mac_backend`、`gaps_vs_cuda`。

## 后端策略

| 优先级 | Backend | 用途 |
|---|---|---|
| 1 | **MLX**（Metal） | checklist 头短训（推荐） |
| 2 | **PyTorch MPS** | 同上，MLX 不可用时 |
| 3 | **CPU numpy** | 协议仍可跑 |
| — | JAX Metal | 探测会标出；**不是** openpi 支持路径 |
| — | CUDA openpi π0 | **Mac 不可跑** |

## 一键

```bash
python3 scripts/rsi/run_local_pipeline.py --mode mac
# 或
python3 scripts/rsi/run_mac_train.py --backend auto --train-steps 200 --parity-check
```

`--parity-check`：确认 Mac 后端与 CPU 路径在 **套件规模 / 指标键** 上协议一致（不要求权重 bit 级相同）。

## 最小依赖（勿 `uv sync` 全量 openpi）

全量 `pyproject.toml` 依赖 `jax[cuda12]`，在 Mac 上会失败。Mac Mini 用轻量 venv：

```bash
uv venv --python 3.12 .venv-mac
source .venv-mac/bin/activate
uv pip install "numpy>=1.26,<2" matplotlib torch mlx pytest
PYTHONPATH=src python scripts/rsi/run_mac_train.py --backend auto --parity-check
```

不要设 `DOWNLOAD_WEIGHTS=1` 去拉 π0 CUDA 权重（本路径用不到）。

## 能做什么 / 不能做什么

**可以**
- 环境探测（芯片 / Metal / MLX / MPS / 内存）
- checklist + gated recovery 短训（MLX/MPS）
- 与 CPU stub 相同的 FIXED_EVAL_SUITE 协议评测（Q-score + E2E）
- `b1k-protocol` 干跑

**不可以（仍需 Linux + CUDA）**
- 官方 `scripts/train.py` π0/π0.5 JAX 微调
- 大权重 `gs://openpi-assets/...` 全量 fine-tune
- 官方 B1K / OmniGibson GPU 仿真榜跑分
- 真机部署

## 与 CUDA 差距（诚实清单）

1. Mac 路径只训 **轻量 checklist 头**，不是 π0 VLA 主干。
2. 评测是 **协议对齐**（同套件、同指标），不是 openpi LIBERO/B1K 官方分数。
3. JAX Metal 即使装上也不是仓库支持的训练栈。
4. 完整 idea→榜单闭环的 GPU 段：见 `rsi/docs/local-gpu-openpi-b1k.md`。

## 产物

- 仓库：`rsi/experiments/mac-silicon-artifacts/`
- Project store 报告镜像：见合入后的 store `docs/mac-silicon-ops.md` / `media/mac-silicon/`
