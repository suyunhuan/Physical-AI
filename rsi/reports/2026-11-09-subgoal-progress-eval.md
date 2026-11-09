# 2026-11-09 · subgoal-progress-eval · 最小验证闭环报告

- 技术路线：R8 安全/恢复/评测（主）+ R2 分层/符号规划（次）
- 绑定短期主线：主线 1（长程任务的子目标分解、规划与执行监控）
- 运行来源：Automation「RSI-单点Idea闭环」手动触发，**触发载荷为空（未携带 idea）**，idea 由本次运行按 `.cursor/rules/rsi-core.mdc` 自行选定
- 结论一句话：评测器核心已落地并通过固定口径验证；**真实 LIBERO 成功率未采集**（无 GPU / 无权重 / 无仿真），本次不声称任何策略性能变化

## 1. 背景与动机

`.cursor/rules/rsi-core.mdc` 硬规则 8 要求：涉及长程任务时必须同时报告端到端任务完成率与子目标（subgoal）级成功率。

但 openpi 当前的 LIBERO 闭环评测完全不具备这个能力。`examples/libero/main.py` 只维护 `total_successes`，成功判定来自 `env.step()` 返回的 `done` 单个布尔值（原文件第 154-158 行、第 176-184 行）。一次失败的长程 rollout 只能得到 `done=False`，无法区分三种本质不同的失败：

1. 完全没有进展（策略不理解任务）；
2. 完成了前几个子目标后卡住（技能缺失或衔接失败）；
3. 曾经达成某个子目标又丢掉（regression，恢复机制的触发信号）。

这个底座是策略无关的：同一套指标后续可以接 TAMP 符号状态、世界模型候选轨迹代价、RL 的 progress reward，或视觉 predicate estimator。因此先把评测口径做对，再谈任何提升。

## 2. 结构基线（已核实）

### 2.1 openpi 侧

| 事实 | 位置 |
|---|---|
| rollout 只统计端到端成功 | `examples/libero/main.py`（改动前）第 74-75、154-158、176-184 行 |
| 无任何 subgoal / predicate 指标 | 同上，全文件 |
| `src/openpi/` 下无 `evaluation` 包 | `src/openpi/` 目录 |
| pytest 只收集 `src` / `scripts` / `packages` | `pyproject.toml` `[tool.pytest.ini_options] testpaths` |
| LIBERO 评测容器是 **Python 3.8**，`PYTHONPATH` 只含 `/app`、`packages/openpi-client/src`、`third_party/libero`，**不含 openpi 主包** | `examples/libero/Dockerfile`（`uv venv --python 3.8`、`ENV PYTHONPATH=...`） |

最后一条决定了模块落点：新代码必须放在 `openpi-client` 包里才能同时被 pytest 收集和被评测容器导入，且必须 Python 3.8 兼容。

### 2.2 LIBERO 侧（本次拉取 submodule 后静态核实）

`third_party/libero` 已按 `.gitmodules` 初始化到 pin 住的 `f78abd68ee283de9f9be3c8f7e2a9ad60246e95c`：

| 事实 | 位置 |
|---|---|
| `done` **就是** BDDL goal 合取式的结果 | `libero/libero/envs/bddl_base_domain.py:807` → `done = self._check_success()` |
| `_check_success()` 对 `parsed_problem["goal_state"]` 的每个 predicate 调 `_eval_predicate` 后做逻辑 AND | 6 个 problem 类文件，实现一致（如 `libero_tabletop_manipulation.py:135-143`） |
| `_eval_predicate` 只处理长度 2（unary）和长度 3（binary）；其他 arity **静默返回 `None`** | 同上 `:145-161` |
| `ControlEnv.env` 持有 problem env，`OffScreenRenderEnv` 继承 `ControlEnv` | `libero/libero/envs/env_wrapper.py:56, 103-104, 152` |

这条链路是本次 idea 的关键依据：逐项读取同一批 predicate，得到的进度轨迹与环境自身的成功位**按构造一致**，所以 `done=True` 时必须全部 atom 为真，可以当一致性自检。

### 2.3 未核实（本次无法运行时验证）

- `parsed_problem["goal_state"]` 的元组布局来自外部 `bddl` 包（未 vendored），五个 suite 上的格式一致性未核实。
- 真实 MuJoCo 下 predicate 是否存在瞬时抖动、每步重复求值的开销、是否有副作用，均未核实。
- 真实 benchmark task 类是否全部与上述 6 个 problem 模板一致，未核实。

因此所有 LIBERO 私有访问都被收在一个适配层里，且全部可注入。

## 3. 改动内容

默认行为零变化：开关 `--report-subgoal-metrics` 默认 `False`，关掉即完整回退。

| 文件 | 性质 | 行数 | 说明 |
|---|---|---|---|
| `packages/openpi-client/src/openpi_client/eval/subgoal_metrics.py` | 新增 | 279 | 通用 tracker / 聚合器，只依赖标准库，不 import LIBERO、JAX 或模型代码 |
| `packages/openpi-client/src/openpi_client/eval/libero_subgoal.py` | 新增 | 88 | LIBERO BDDL 适配层，鸭子类型，`goal_provider` / `predicate_evaluator` 均可注入 |
| `packages/openpi-client/src/openpi_client/eval/subgoal_metrics_test.py` | 新增 | 183 | 18 条单元测试 |
| `packages/openpi-client/src/openpi_client/eval/libero_subgoal_test.py` | 新增 | 106 | 8 条单元测试 |
| `scripts/subgoal_metrics_replay.py` | 新增 | 153 | 确定性 scripted 回放，固定期望值，不匹配即非零退出 |
| `examples/libero/main_test.py` | 新增 | 222 | 桩环境集成测试，覆盖真实 `eval_libero` 循环 |
| `examples/libero/main.py` | 修改 | +135 / -4 | 接入开关、每步采样、JSONL + summary 落盘 |

`examples/libero/main.py` 的具体改动：

- `Args` 新增 `report_subgoal_metrics: bool = False` 与 `subgoal_metrics_out_path: str`。
- 新增 `_sample_goal_atoms()`：采样失败时**返回原因而不抛出**，调用方丢弃 tracker 并继续 rollout，避免把评测器故障记成策略失败。
- rollout 循环内：warm-up 结束后、首个 policy action 之前采一次基线（step 0）；每个 policy action 之后采一次。`done` 的判定逻辑完全未改。
- episode 结束后 finalize，写一行 JSONL；suite 结束写 summary JSON，并在 instrumentation coverage < 1 或出现 `done_atom_mismatch` 时打 error 日志。
- 顺带把 `done = False` 在 episode 开头初始化（原代码若首步即异常，后面 `suffix = "success" if done else "failure"` 会 `NameError`）。这一行是结构化 finalize 的前提，不是无关重构。
- 加了 `from __future__ import annotations`，因为评测容器是 Python 3.8。

## 4. 固定评测口径

设 episode $e$ 有 $N_e$ 个 goal atom，采样时刻 $t=0$ 为 warm-up 结束后的基线，$t>0$ 为第 $t$ 个 policy action 之后。warm-up 步不采样，所以掉落物体不会被记成进度或 regression。状态 $g_{e,i,t}\in\{0,1\}$。

| 指标 | 定义 |
|---|---|
| 端到端完成率 | $\frac{1}{E}\sum_e \mathbf{1}[\text{env done}]$，异常与超时均计失败，不从分母剔除 |
| subgoal 成功率（episode） | $\frac{1}{N_e}\sum_i \max_t g_{e,i,t}$（ever achieved） |
| subgoal 成功率 macro / micro | macro = episode 等权；micro = atom 等权（偏向 atom 多的任务）；**两者都报** |
| 瞬时进度 | $p_{e,t}=\frac{1}{N_e}\sum_i g_{e,i,t}$，报 `final_progress` / `max_progress` / `progress_auc`（对 $t$ 取均值） |
| 首次达成步数 | $\tau_{e,i}=\min\{t\mid g_{e,i,t}=1\}$，未达成记 `null`，**不填 max_steps**；均值只对已达成 atom 求，并同时报 `achieved_atom_coverage` |
| regression | 存在 $g_{e,i,t-1}=1 \wedge g_{e,i,t}=0$；报 atom 级比率、episode 级比率、transition 计数、首次 regression 步 |
| 一致性自检 | `done_atom_mismatch` = env 报成功但末步存在 atom 为假；非零即说明 atom 读数不可信，该轮口径作废 |
| 仪表覆盖率 | `instrumentation_coverage` = 已插桩 episode / 全部 episode；< 1 时 subgoal 数字只描述子集，必须显式披露 |

## 5. 本次实际跑了什么（全部在 CPU，可复现）

```bash
export PATH="$HOME/.local/bin:$PATH"
cd /agent/repos/Physical-AI
git submodule update --init third_party/libero     # 仅为静态核实 LIBERO 源码
uv venv --python 3.11 && uv sync --group dev

# 1) 单元测试：26 passed
JAX_PLATFORMS=cpu uv run pytest -q packages/openpi-client/src/openpi_client/eval

# 2) 桩环境集成测试（真实 eval_libero 循环）：5 passed
JAX_PLATFORMS=cpu uv run pytest -q examples/libero/main_test.py

# 3) 确定性回放（固定口径）：14 个聚合字段全部匹配
JAX_PLATFORMS=cpu uv run python scripts/subgoal_metrics_replay.py

# 4) 既有测试回归：70 passed
JAX_PLATFORMS=cpu uv run pytest -q packages src/openpi/transforms_test.py \
  src/openpi/training/data_loader_test.py src/openpi/shared

# 5) 静态检查：全部通过
uv run ruff check examples/libero scripts/subgoal_metrics_replay.py \
  packages/openpi-client/src/openpi_client/eval
uv run ruff format --check examples/libero scripts/subgoal_metrics_replay.py \
  packages/openpi-client/src/openpi_client/eval

# 6) Python 3.8 兼容性（评测容器口径）
uv venv --python 3.8 /tmp/py38
PYTHONPATH=packages/openpi-client/src /tmp/py38/bin/python -c "from openpi_client.eval import libero_subgoal"
```

### 5.1 结果

| 项 | 结果 |
|---|---|
| 新增单元测试 | **26 passed**（`subgoal_metrics` 18 + `libero_subgoal` 8） |
| 桩环境集成测试 | **5 passed**（默认关闭不落盘 / 原子追踪 / 重跑不追加 / goal 不可读记为未插桩 / predicate 失败不中断 rollout） |
| 确定性回放 | **匹配**，14 个聚合字段 + 两组 `first_achieved_step` 全部与手算一致 |
| 既有测试回归 | **70 passed**，无新增失败 |
| ruff check / format | **通过** |
| Python 3.8 导入与运行 | **通过**（CPython 3.8.20） |

### 5.2 回放固定口径数值（手算核对，非程序自证）

两条 scripted episode：A 三个 atom，轨迹 `000 → 100 → 110 → 010 → 111`，end-to-end 成功；B 两个 atom，轨迹 `00 → 10 → 10`，失败。

| 指标 | 期望（手算） | 实测 |
|---|---|---|
| 端到端成功率 | 1/2 = 0.5 | 0.5 |
| subgoal micro | (3+1)/(3+2) = 0.8 | 0.8 |
| subgoal macro | (1.0+0.5)/2 = 0.75 | 0.75 |
| progress AUC macro | (7/15 + 1/3)/2 = 0.4 | 0.4 |
| regressed atom rate | 1/5 = 0.2 | 0.2 |
| episode regression rate | 1/2 = 0.5 | 0.5 |
| first_achieved_step | `[1,2,4]` / `[1,null]` | 一致 |

注意 episode A：端到端成功率和 subgoal 成功率都是满分，但它在 $t=3$ 丢掉了 atom 0。**只有 regression 指标能暴露这件事**，这正是本次改动的价值点。

## 6. 阻塞项（本次采不到的指标，如实披露）

| 采不到的指标 | 阻塞原因 |
|---|---|
| 真实 LIBERO 固定 suite 的端到端成功率 | 本机无 GPU（`nvidia-smi` 不存在）、无 pi0/pi0.5 权重、LIBERO/robosuite/MuJoCo 未安装 |
| 真实策略的 subgoal 成功率 / progress / first-step / regression | 同上 |
| 五个 suite 的 adapter 覆盖率、predicate 抖动率、每步求值开销 | 需要运行中的仿真器 |
| **CPU `debug` 配置训练回归烟雾测试** | **基线即失败**：`JAX_PLATFORMS=cpu uv run pytest -q scripts/train_test.py` 在**未改动代码的情况下**被 cgroup OOM kill（exit 137，`dmesg`：`Killed process ... anon-rss:13996344kB`），重试并限制 `OMP_NUM_THREADS=1` 仍然 137。根因：`src/openpi/models/pi0.py:84` 把 SigLIP 图像塔硬编码为 `So400m/14`（约 400M 参数），`paligemma_variant="dummy"` 只缩小 LLM 不缩小视觉塔；float32 的参数 + 梯度 + Adam 动量在 15GB / 4 vCPU 的机器上放不下。这是**环境限制，不是本次改动引入的回归**。 |

替代证据：本次改动新增的是一个独立子包 `openpi_client.eval`，`src/openpi` 与 `scripts/train.py` 中无任何文件 import 它（已用 `rg` 核实：`src/openpi` 只 import `openpi_client` 的 `image_tools` / `base_policy` / `msgpack_numpy`），且导入 `openpi_client` 的既有测试（`transforms_test`、`data_loader_test`）全部通过。训练路径无接触面。

## 7. 结论

- **值得继续。** 评测器核心（指标定义、聚合、异常会计、LIBERO 适配层的解析与校验、`eval_libero` 的接入逻辑）已在 CPU 上真实验证，Python 3.8 兼容性已验证，默认关闭、改动可完整回退。
- **不能声称的事情**（本次证据不支持）：
  - 不能声称已满足硬规则 8 的真实评测要求 —— 只验证了评测器，没有跑过真实 rollout。
  - 不能声称 BDDL goal atoms 是真实的规划子目标 —— 它们是无序的 symbolic goal atoms，没有前置条件和技能映射，只能用于执行监控。
  - 不能声称 adapter 已覆盖全部 LIBERO suite。
  - 不能声称任何模型成功率的提升或劣化 —— 本次没有训练、没有推理、没有仿真。
  - 不能声称 regression 信号可直接触发可靠恢复 —— 本次只提供监控信号。

## 8. 风险与下一步

### 风险

1. **依赖 LIBERO 私有 API**：`env.env`、`parsed_problem`、`_eval_predicate` 都不是公共接口。已全部收在 `libero_subgoal.py` 一个文件里并可注入，但 LIBERO 升级仍可能打断。
2. **predicate 非单调**：物体可能短暂进入目标区域后掉出，所以必须同时看 ever-achieved、final progress 和 regression，单看任何一个都会误判。
3. **micro / macro 口径偏差**：micro 偏向 atom 多的任务。两者都报，解读时必须指明用的是哪个。
4. **goal atom 被过度解释为规划子目标**：报告与代码注释都已明确限定为执行监控原子。
5. **重复求值开销与副作用未知**：因此默认关闭，必须在真实仿真上验证后再考虑改默认值。

### 下一步（按预期收益排序）

1. 在有 GPU + 权重 + LIBERO 的机器上，用固定 suite 跑一次 `--report-subgoal-metrics`，首要看 `done_atom_mismatch_episodes == 0` 与 `instrumentation_coverage == 1.0`；只有这两项成立，后续 subgoal 数字才可用。
2. 核实五个 suite 的 `goal_state` 格式一致性与每步求值开销；若开销显著，改为每 K 步采样并在口径里写明 K。
3. 上述通过后，再把 `report_subgoal_metrics` 默认值改为 `True`，使硬规则 8 在真实评测中默认生效。
4. 把 regression 信号接到失败恢复（R8）或 progress reward（R4）之前，先补一轮「regression 是否可靠」的测量，不要直接当奖励用。
