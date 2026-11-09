# 报告 · 轮式双臂家庭长程最小闭环（dry-run）

- 日期：2026-11-09
- slug：`wheeled-bimanual-household-minloop`
- 分支：`cursor/bc-fc7bcb31-2b8d-4272-af9f-79241aefc45c-367d`
- 协议：轮式双臂家庭最小闭环，**默认 dry-run（文档与脚本级）**
- 执行档位：输入未写「允许训练 / 允许拉权重」，因此**未下载任何模型权重、未做任何 GPU 训练、未做任何真机部署**
- 计划：[2026-11-09-wheeled-bimanual-household-minloop.md](../plans/2026-11-09-wheeled-bimanual-household-minloop.md)

## 0. 一句话结论

**仿真闭环本轮跑不了**：本 VM 无 GPU，仓库里没有任何 OmniGibson / BEHAVIOR-1K / BDDL / 轮式双臂代码，`third_party/{libero,aloha}` submodule 未 checkout，openpi 依赖未安装。
本轮交付的是**可批准的规划 + 可本地运行的 dry-run 校验**：`wheeled_bimanual_v0` 20 维动作 schema 已被脚本机械校验与 openpi 现有契约一致。
**没有任何指标被测量，`rsi/leaderboard.md` 保持空榜。**

## 1. 协议步骤执行情况

| 步骤 | 要求 | 实际 |
|---|---|---|
| 1 | 读 `rsi/leaderboard.md` 与批准的 plan | **两者原本都不存在**：仓库只有 `rsi/{daily,plans,reports}` 空目录 + 空模板 `experiment-tree.md`。无法「读取已批准 plan」，故本轮产出 plan 草案并新建 leaderboard 骨架，二者均标注待批准 / 空榜 |
| 1 | 确认形态与指标 | 形态 = 轮式底盘 + 升降躯干 + 双 7-DoF 臂 + 双夹爪；场景 = 家庭长程（5-15 subgoal）；主指标 = BDDL goal-literal 部分学分（本仓库命名为 `LPC`）+ 端到端成功率 + subgoal 成功率 |
| 2 | planner 输出仿真入口 / 数据配方 / 评测命令 / 接口缝隙 | 已完成，见 plan 第 2-5 节 |
| 3 | 不可跑仿真则输出阻塞清单与人工项 | 已完成，见本报告第 4 节 |
| 4 | 可干跑则只做环境探测 / 配置校验 / 小规模 dry-run | 已完成，见第 3 节（新增 `scripts/rsi/wheeled_bimanual_preflight.py`） |
| 5 | 报告 + 四元组 + leaderboard log | 本文件 + `rsi/experiments/experiment-tree.md` + `rsi/leaderboards/log.md` |
| 6 | 独立分支开 PR，verifier 未过不得标 ready | 本轮在独立分支提交并开 PR；**不标 ready for review** |

### 输入说明（必须披露）

触发本轮的 webhook **请求体为空**（`bodyDigest` 为空串的 sha256），没有携带任何待验证数据或具体的形态假设文本。
因此「输入的数据 × 形态假设 H」中的 H **取自协议第 1 步给定的形态定义**（轮式底盘 + 双臂 + 家庭长程），
并且**没有任何外部输入数据集参与**。本轮不存在「对输入数据做处理」的环节。

## 2. 形态假设 H 与指标口径

H：轮式移动底盘（holonomic 或 differential）+ 升降躯干 + 双 6-7 DoF 手臂 + 双夹爪，执行多房间取物 / 收纳 / 清洁 / 厨房辅助，单任务 5-15 个有序子目标。

主指标（口径细节见 plan §4.5）：

- `LPC`（literal partial credit）：**终止状态**下满足的 BDDL goal literals 占比，禁止 max-over-time 抬分。
  **官方「Q-score」的精确定义本轮未核实，故不冒用该名称。**
- 端到端成功率：成功 episode / 全部排程 episode；崩溃、超时、安全终止一律计失败。
- Subgoal 成功率：按规划顺序首次达到，报 `SGSR_micro` / `SGSR_macro` 与逐位置 `SG1…SG15`。

## 3. 本轮实际跑过的东西（dry-run）

新增 `scripts/rsi/wheeled_bimanual_preflight.py`：纯标准库，不装依赖、不联网、不拉权重、不训练。
它只做本地探测与仓库内文件的静态读取，并机械校验 `rsi/plans/wheeled_bimanual_v0_schema.json`。

### 3.1 运行结果

```text
python3 scripts/rsi/wheeled_bimanual_preflight.py
# failed=0 blocked=9 total=22   (12 PASS / 9 BLOCKED / 1 INFO)   exit=0
```

首次运行（创建 plan 与 leaderboard 之前）为 `failed=0 blocked=12`；补齐 `rsi/leaderboard.md`、`rsi/leaderboards/log.md`、
`rsi/plans/*.md` 后降至 `blocked=9`，剩余 9 项全部是 GPU / 依赖 / 仿真器类硬阻塞。

### 3.2 PASS 的 12 项（即本轮真正被验证的事实）

| 检查 | 结论 |
|---|---|
| `env.python` | Python 3.12.3 满足 `requires-python >=3.11` |
| `mask.replica` | 脚本内 `make_bool_mask` 复制件复现了 `src/openpi/transforms.py` 两条 docstring 示例；上游语义若变更会直接 FAIL |
| `repo.configs` | 参照 config `pi05_libero` / `pi0_aloha` / `pi05_droid` 确实注册在 `src/openpi/training/config.py` |
| `repo.image_slots` | `base_0_rgb` / `left_wrist_0_rgb` / `right_wrist_0_rgb` 三槽位名在 `src/openpi/policies/libero_policy.py` 中存在，且 schema 对三者均有传感器映射 |
| `schema.action_dim` | 物理 20 维装入 `action_dim=32`，余 12 维 padding |
| `schema.layout` | 6 个字段恰好铺满索引 0..19，无重叠、无空洞、无越界 |
| `schema.action_space` | 每个字段都显式声明 delta 或 absolute |
| `schema.delta_mask` | `make_bool_mask(-3, 8, -1, 7, -1)` 与逐字段声明完全一致（delta 字段 = 躯干升降、左臂、右臂） |
| `rsi.leaderboard` / `rsi.log` / `rsi.experiment-tree` / `rsi.plans` | 四个登记位均已存在 |

### 3.3 反向验证（证明校验器不是「一律 PASS」）

对 schema 注入 4 种人为错误后重跑，全部被捕获且 `exit=1`：

| 注入的错误 | 捕获的输出 |
|---|---|
| 右臂起点改为 11（与左夹爪重叠） | `FAIL schema.layout: right_arm_joints collides with left_gripper at index 11; unassigned indices [18]` |
| `delta_mask_spec` 改为底盘做 delta | `FAIL schema.delta_mask: delta_mask_spec disagrees with per-field action_space at indices [0, 1, 2]` |
| `model_action_dim` 改为 16 | `FAIL schema.action_dim: physical_dim 20 exceeds model action_dim 16` |
| 参照 config 改为不存在的 `pi99_not_real` | `FAIL repo.configs: reference configs absent from config.py: pi99_not_real` |

正确 schema 返回 `exit=0`，四个错误 schema 全部返回 `exit=1`。

### 3.4 明确没做的事

- 未安装 uv、未安装 openpi 依赖、未 `uv sync`。
- 未初始化任何 submodule。
- 未下载任何 checkpoint / 权重 / 数据集。
- 未启动 `scripts/serve_policy.py`，未运行 `examples/libero/main.py`。
- 未跑任何仿真 rollout，未产生任何 LPC / 成功率 / subgoal 数字。
- 未触碰任何真机。

## 4. 阻塞清单与人工项

| # | 阻塞 | 影响 | 需要谁做什么 |
|---|---|---|---|
| 1 | 无 NVIDIA GPU（`nvidia-smi` 不存在），4 vCPU / 15GB RAM | pi0 推理与 Isaac Sim / OmniGibson 都跑不了 | 基础设施：提供匹配驱动、CUDA、显存与磁盘的 GPU 主机 |
| 2 | 仿真器未选定且全部未安装（omnigibson / bddl / libero / mani_skill / habitat 均 import 失败） | 没有任何可执行的长程评测环境 | 仿真负责人：选定一个入口并钉死版本 |
| 3 | Isaac Sim / OmniGibson 版本矩阵、许可证、安装体积未核实 | 无法给出可复现安装方案 | 仿真负责人：核实官方版本矩阵、许可、容器与资产下载规模 |
| 4 | **轮式双臂资产是否存在未核实**（Tiago++ / Galaxea R1 / HSR 双臂 / Fourier / Unitree 轮式双臂；Fetch 常见形态非双臂） | 资产缺失则 H 根本无法验证 | 机器人/仿真负责人：逐一验证资产，**不得按名称推断双臂能力**；缺失则导入 URDF/USD + 控制器 + 传感器 |
| 5 | BDDL goal-literal 评测器与官方 Q-score 定义未核实 | 无法计算协议要求的部分学分 | 评测负责人：确认 canonical predicate evaluator 与 Q-score 公式；未确认前只报 `LPC` |
| 6 | `third_party/libero`、`third_party/aloha` 未 checkout | 现有仿真示例不可运行 | 仓库维护者：`git submodule update --init --recursive` 并记录 commit |
| 7 | 无 uv、openpi 依赖未安装（`import openpi` 失败） | 无法执行任何 config / transform / 单测 | 环境负责人：装 uv，按锁文件建 Python 3.11 环境 |
| 8 | 禁止拉权重且无本地 checkpoint | `serve_policy.py` 无策略可载 | 模型负责人：在另一个获批环境准备合法本地 checkpoint；本轮只能 mock policy |
| 9 | `household_long_v0` manifest、固定初始状态、subgoal 谓词未冻结 | 结果不可比较 | 任务负责人：冻结任务集、goal literals、subgoal、seed、超时并记录 hash |
| 10 | planner / monitor / 安全层尚无实现 | 只有低层 action chunk，不构成长程闭环 | 规划负责人：提供确定性非 VLA 基线 B0，定义 monitor 状态机与恢复预算 |
| 11 | 无轮式双臂 LeRobot 数据 | 无法适配或训练目标形态 | 数据负责人：提供 schema 合规轨迹、坐标单位、subgoal sidecar、固定 split |
| 12 | 本轮无已批准 plan（`rsi/plans/` 原为空） | 不满足 RSI 实验启动门槛 | 项目负责人：审批本轮 plan 草案的预算、停止条件与回退点 |

## 5. 四元组

| 字段 | 内容 |
|---|---|
| 假设 | 轮式底盘 + 升降躯干 + 双 7-DoF 臂形态上，分层闭环（规划器 + openpi 子目标技能 + 执行监控）在家庭长程任务上优于端到端单指令 VLA；且固定底座预训练存在可量化的 cross-embodiment gap |
| 改动 | 仅文档与脚本级：plan 草案、`wheeled_bimanual_v0` 20 维 schema（JSON）、纯标准库 dry-run 校验器、leaderboard 骨架。**openpi 代码零改动** |
| 指标 | LPC（终止状态 BDDL literal 部分学分）+ 端到端成功率 + subgoal 成功率（micro/macro + 逐位置）。**本轮全部未测量** |
| 失败原因 / 结论 | 未进入实验阶段即被环境阻塞：无 GPU、仿真器未选定且未安装、轮式双臂资产未核实、无已批准 plan、无本地 checkpoint。结论只覆盖「schema 与 openpi 现有动作/图像契约机械一致」，**不覆盖任何性能声明** |

## 6. 复现命令

```bash
# 本轮全部可复现内容（无需任何依赖、不联网）
python3 scripts/rsi/wheeled_bimanual_preflight.py
python3 scripts/rsi/wheeled_bimanual_preflight.py --json
```

## 7. 下一步

按 plan §7 的门槛推进：冻结 schema 与 manifest → CPU 合约模拟器跑通闭环与日志 → GPU 主机上做 LIBERO 链路冒烟 →
确认目标仿真器与轮式双臂资产后接入 B1/B2 并首次上报指标。**只有最后一步完成才允许向 `rsi/leaderboard.md` 写入成绩。**
