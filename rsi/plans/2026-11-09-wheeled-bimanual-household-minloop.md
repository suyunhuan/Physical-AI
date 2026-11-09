# 计划 · 轮式双臂家庭长程最小闭环（household-minloop）

- 日期：2026-11-09
- 形态假设 H：轮式移动底盘 + 升降躯干 + 双 7-DoF 手臂 + 双夹爪
- 场景：家庭长程任务（多房间取物 / 收纳 / 清洁 / 厨房辅助），单任务 5-15 个子目标
- 主指标：BDDL goal-literal 部分学分（LPC）+ 端到端成功率 + subgoal 成功率
- 状态：**待批准（draft）**。本计划未经人工批准前，不得执行任何 rollout，也不得上报任何成绩。
- 规划来源：planner subagent（只读），事实项由本仓库代码核实，外部事实一律标注「未核实」

标注约定：**【事实】** 已在本仓库核实 ｜ **【方案】** 建议做法，仓库尚无实现 ｜ **【未核实】** 外部事实/资产/版本尚未验证

---

## 1. 问题定义与技术路线归类

### 1.1 问题定义

在轮式双臂形态上同时回答五个问题：任务能否端到端完成；哪些 subgoal 完成/失败/回退；终止时满足多少 BDDL goal literals；失败后能否检测与恢复；固定底座预训练 VLA 能否迁移到移动双臂形态。

**【方案】最小闭环链路：**

```text
固定任务 manifest
  → 高层任务/子目标规划器
  → 当前子目标与技能参数
  → openpi VLA 或非 VLA 技能控制器
  → 动作安全过滤
  → 仿真执行 action chunk
  → 谓词 / 场景状态 / 超时监控
  → 成功则推进子目标；失败则重试 / 重规划 / 安全终止
  → 固定评测器汇总 LPC、端到端、subgoal 指标
```

必须保留三条可比较基线，禁止只跑 VLA：

| 基线 | 构成 | 作用 |
|---|---|---|
| B0 非 VLA | 符号 / TAMP 规划器 + 仿真器原生或脚本技能 | 确定性下界，验证评测器本身可用 |
| B1 分层 VLA | 同一规划器 + openpi 子目标条件技能策略 | 主方案 |
| B2 端到端 VLA | 只给长程总指令，不给显式子目标 | 检验分层的增益是否真实 |

### 1.2 R1-R8 归类

| 路线 | 定位 | 绑定主线 | 职责 |
|---|---|---|---|
| R2 分层/符号规划 | **主路线** | 规划执行监控 | 任务分解、前置条件、技能选择、重规划 |
| R8 安全/恢复/评测 | **主路线** | 规划执行监控 | 谓词监控、超时、动作约束、失败分类、固定口径 |
| R1 VLA/端到端 | 主要技能路线 | 规划执行监控 | 执行当前子目标；与 B0/B2 对照，不得是唯一方案 |
| R5 数据/仿真 | 次路线 | 数据效率与泛化评测 | LeRobot 转换、仿真示范、场景扰动、任务/形态划分 |
| R7 基础模型/跨形态 | 次路线 | 数据效率与泛化评测 | 固定底座 → 轮式双臂的迁移差距 |
| R6 感知/记忆 | 次路线 | 规划执行监控 | 房间图、对象身份、遮挡重定位；MVP 用仿真真值取上界 |
| R3 世界模型/MPC | 后续候选 | 规划执行监控 | 候选技能 / 底盘路径短视界预测 |
| R4 RL/自改进 | 后续候选 | 数据效率与泛化评测 | 失败轨迹离线重加权、恢复策略；本轮不训练 |

### 1.3 当前结构基线

- **【事实】** openpi 已有 VLA 模型、LeRobot/RLDS 数据配置、policy 适配层、WebSocket 服务、LIBERO 客户端。
- **【事实】** 现有适配层（`libero_policy.py` 8 维 state / 7 维输出、`aloha_policy.py` 14 维双臂固定底座、`droid_policy.py` 7+1 维单臂）均不覆盖「移动底盘 + 双臂 + 长程 BDDL 监控」。
- **【事实】** `examples/libero/main.py` 只按环境 `done` 统计整任务成功，没有 goal-literal 部分学分或 subgoal 轨迹。
- **【事实】** 全仓 grep 无 OmniGibson / BEHAVIOR-1K / BDDL / Q-score / 轮式 / bimanual 相关代码或文档。
- **【方案】** 首轮只验证接口闭环、指标口径和 VLA/非 VLA 可替换性，不把训练效果作为验收条件。

---

## 2. 仿真入口候选

外部仿真器的版本、许可证、机器人资产与 API 全部 **【未核实】**，选型后须按固定版本文档复核。

| 候选 | 形态匹配 | 长程 / BDDL | 硬件门槛 | 接入成本 | 本仓库可达性 |
|---|---|---|---|---|---|
| BEHAVIOR-1K / OmniGibson | 潜在最高（取决于轮式双臂资产） | 最匹配 | 高 | 中高 | 当前不可达 |
| ManiSkill | 中（移动双臂资产未核实） | 无可见 BDDL 接口 | 中 | 中 | 未接入 |
| RoboCasa + robosuite | 中低（偏固定底座厨房） | 可构造长程，原生 BDDL 未核实 | 中 | 中 | 未接入 |
| Habitat 3.0 | 导航匹配，双臂操作未核实 | 长程移动较合适，BDDL 未核实 | 中高 | 高 | 未接入 |
| LIBERO | 低（固定底座、单臂 7 维） | 有 BDDL 文件，但现评测只用 `done` | 中 | **低** | submodule 初始化后最接近可用 |
| AI2-THOR + ALFRED | 低（抽象动作，非连续双臂动力学） | 高层长程强，Q-score 不匹配 | 低 | 中 | 未接入 |
| CPU 合约模拟器 | 无物理，仅验证接口 | 可本地实现谓词状态机 | **低** | **低** | 最适合本 VM 首轮 |

### 2.1 BEHAVIOR-1K / OmniGibson（最终候选）

- **【未核实】** 对 Isaac Sim、NVIDIA 驱动与 GPU 的硬依赖；支持版本、显存与安装体积。
- **【未核实】** BDDL goal literals 的部分学分聚合方式；官方「Q-score」的精确定义与否定 literal 处理。
- **【未核实】** 轮式双臂资产是否内置：Tiago/Tiago++、Fetch（常见形态通常非双臂，不能直接验证 H）、Galaxea R1、HSR 双臂变体、Fourier/Unitree 轮式双臂 —— 逐一都需验证，**不得按名称推断双臂能力**。
- 接入需把仿真观察转为三路图像槽位 + 20 维 state，并把输出转为底盘速度与关节/夹爪控制。
- 它是终局入口，但不适合作为本 VM 的首个可执行入口。

### 2.2 卫星栈推进顺序

1. **CPU 合约模拟器（首选）**：只实现任务状态机、三路伪图像、20 维状态、动作裁剪、subgoal 谓词与失败注入。不产生任何物理性能结论。
2. **LIBERO 链路冒烟**：验证「服务端—客户端—环境—日志」链路；可先扩展 literal/subgoal 记录。**不能证明 H**。
3. **操作技能卫星（ManiSkill / RoboCasa）**：局部技能数据与恢复测试。
4. **导航/记忆卫星（Habitat 3.0 / AI2-THOR）**：多房间导航与对象记忆；抽象动作结果不得冒充连续双臂控制结果。
5. **BEHAVIOR-1K / OmniGibson**：待固定版本、GPU、许可证、目标资产、官方评测器全部确认后进入。

---

## 3. 数据配方

### 3.1 20 维 state/action 布局 `wheeled_bimanual_v0`

机器可读定义见 `rsi/plans/wheeled_bimanual_v0_schema.json`，由 `scripts/rsi/wheeled_bimanual_preflight.py` 校验。

| 索引 | 维度 | 内容 | 动作语义 |
|---|---:|---|---|
| `0:3` | 3 | 底盘速度 `vx, vy, wz` | 绝对；差分底盘强制 `vy=0` |
| `3` | 1 | 躯干升降 | 增量 |
| `4:11` | 7 | 左臂关节 | 增量 |
| `11` | 1 | 左夹爪 | 绝对 |
| `12:19` | 7 | 右臂关节 | 增量 |
| `19` | 1 | 右夹爪 | 绝对 |
| `20:32` | 12 | 零 padding | 不发送给仿真器 |

对应掩码 `_transforms.make_bool_mask(-3, 8, -1, 7, -1)`。

- **【事实】** `make_bool_mask` 正数展开为 `True`、非正数展开为 `False`（`src/openpi/transforms.py:433`）。
- **【事实】** `DeltaActions` 对 mask 为 `True` 的维度减去当前 state，`False` 维度保持绝对（`src/openpi/transforms.py:204`）。
- **【风险】** 该变换假定 action 与 state 的同索引语义一致。因此底盘槽位必须固定为速度语义；全局位姿放外部 monitor，**不塞入这 20 个控制槽**。
- **【方案】** 6-DoF 双臂须另立 18 维 schema，或在 20 维中明确锁定两个虚拟关节并从损失与输出中排除；不得当作普通训练维度。

### 3.2 图像映射

| openpi 固定槽位 | 轮式双臂传感器 |
|---|---|
| `base_0_rgb` | 头部/躯干前视 RGB（需同时覆盖导航与工作区） |
| `left_wrist_0_rgb` | 左腕 RGB |
| `right_wrist_0_rgb` | 右腕 RGB |

- **【事实】** 三槽位命名与 mask 规则见 `src/openpi/policies/libero_policy.py`；缺图时 π0/π0.5 置零并 mask `False`，π0-FAST 沿用 `True`。
- **【方案】** 深度、分割、地图与 3D scene graph 不占用这三个 RGB 槽，由外部感知/记忆模块消费或离线编码进 planner 状态。

### 3.3 LeRobot 字段与长程元数据

```text
observation.images.base / .left_wrist / .right_wrist
observation.state   float32[20]
action              float32[20]
task                当前技能 / 子目标语言
```

长程元数据用 sidecar manifest（按 `episode_id` + frame range）：`parent_task_id`、`high_level_instruction`、`subgoal_id`、`subgoal_text`、`subgoal_start_frame`、`subgoal_end_frame`、`goal_literals`、`failure_type`、`recovery_id`、`scene_id`、`object_split`、`embodiment_id`。

采用 sidecar 是为避免假设当前 LeRobot 版本支持任意嵌套 BDDL 结构（**【未核实】**）；确认支持后再迁入正式 feature。

### 3.4 转换脚本参照

- 双臂多相机布局：`examples/aloha_real/convert_aloha_data_to_lerobot.py`
- 最小 `LeRobotDataset.create/add_frame/save_episode`：`examples/libero/convert_libero_data_to_lerobot.py`
- **【方案】** 新脚本保留完整长程 episode；训练低层技能时按 subgoal frame range 切子 episode 并令 `task=subgoal_text`。高层 planner 用完整任务 + sidecar；低层 VLA 只接收当前子目标，避免要求单个 action chunk 覆盖 5-15 个目标。

### 3.5 固定数据划分

seen scene/object、unseen scene、unseen object、unseen task composition、cross-embodiment、无恢复 vs 允许恢复。归一化统计必须只用训练 split；padding 维度不得参与物理指标，且须验证不污染 norm stats 与训练损失。

---

## 4. 评测命令草案

以下为草案，**本轮不执行**。

### 4.1 只读 preflight（本 VM 可执行）

```bash
python3 scripts/rsi/wheeled_bimanual_preflight.py
python3 scripts/rsi/wheeled_bimanual_preflight.py --json
```

### 4.2 获批后的环境准备（本 VM 不可执行：无 uv）

```bash
git submodule update --init --recursive
uv venv --python 3.11
GIT_LFS_SKIP_SMUDGE=1 uv sync
GIT_LFS_SKIP_SMUDGE=1 uv pip install -e .
uv run python -c "import openpi; print(openpi.__file__)"
uv run scripts/serve_policy.py --help
uv run examples/libero/main.py --help
```

**【事实】** `pyproject.toml` 的 `rlds` 组注释指明 `tensorflow-cpu==2.15.0` 只有 cp311 wheel，故固定 Python 3.11；目标仿真器支持的 Python 版本 **【未核实】**。

### 4.3 现有 LIBERO 链路（链路冒烟，不验证 H）

```bash
uv run scripts/serve_policy.py policy:checkpoint \
  --policy.config=pi05_libero \
  --policy.dir=/absolute/path/to/local/checkpoint \
  --port=8000

uv run examples/libero/main.py \
  --host=127.0.0.1 --port=8000 \
  --task-suite-name=libero_10 \
  --num-trials-per-task=50 --seed=7 --replan-steps=5
```

**当前不可执行原因**：无 uv；openpi 依赖未装；LIBERO submodule 未 checkout；无本地 checkpoint；默认 checkpoint 会触发权重下载（本轮禁止）；无 GPU。

### 4.4 计划中的轮式双臂入口（**方案，非现有 API**）

```bash
uv run examples/wheeled_bimanual/main.py \
  --host=127.0.0.1 --port=8000 \
  --suite-manifest=/absolute/path/to/household_long_v0.json \
  --seed-set=7,17,27,37,47,57,67,77,87,97 \
  --trials-per-task=10 --replan-steps=5 \
  --controller=hierarchical_vla \
  --metrics-out=/absolute/path/to/results.jsonl
```

仿真器启动命令须等固定版本文档确认后填写，**不得预先编造 OmniGibson API**。

### 4.5 固定上报口径

评测集：suite `household_long_v0`（**尚未冻结**）、10 个固定任务实例、每任务 10 个固定初始状态、seed `[7,17,27,37,47,57,67,77,87,97]`、每任务 5-15 个冻结有序 subgoal。manifest、BDDL 文件、初始状态、对象/场景版本与判定器均记录 hash；对比实验必须同 episode 列表、同动作频率、同超时、同恢复预算。

**Literal partial credit（LPC）**

```text
LPC_e = |{ l ∈ G_e : canonical evaluator 在终止状态判定 l 为真 }| / |G_e|
```

- 只在**终止状态**计算，禁止用「曾经满足过」抬分。
- 正、负 literal 均由固定 canonical evaluator 判定。
- 官方 Q-score 定义未核实前，只报 `LPC`，**不得冒称官方 Q-score**。
- 报告 episode micro mean、task macro mean 与逐任务结果。

**端到端成功率**：`E2E = 成功 episode / 全部排程 episode`。缺失、崩溃、超时、安全终止均计失败，不得从分母删除。

**Subgoal 成功率**：每个 subgoal 由冻结谓词集合定义，须按规划顺序首次达到；记录 `achieved_at_step`，保持型谓词按 manifest 指定连续 N 步确认。报告 `SGSR_micro`（完成有序 subgoal / 全部计划 subgoal）、`SGSR_macro`（先 episode 再任务等权）以及每个位置 `SG1…SG15` 的成功率与失败类型。

---

## 5. 与 openpi 的接口缝隙

### 5.1 可直接落到 openpi 文件级

| 文件 / 类 | 输入输出契约 | 主要风险 |
|---|---|---|
| 新增 `src/openpi/policies/wheeled_bimanual_policy.py` | `WheeledBimanualInputs`：三路 RGB + `state[20]` + prompt → openpi 公共格式；`WheeledBimanualOutputs`：`actions[...,32]` → 截取前 20 维 | 索引顺序、单位、动作范围、π0-FAST mask 规则 |
| 修改 `src/openpi/training/config.py` | 新增 `LeRobotWheeledBimanualDataConfig`，Repack 三路图像/state/action，应用 `make_bool_mask(-3,8,-1,7,-1)` | `DeltaActions` 与 state 语义错位；norm stats 污染 |
| 修改 `config.py` 的 `_CONFIGS` | 新增 `pi05_wheeled_bimanual` 等 `TrainConfig`，保持 `action_dim=32`，物理动作 20 维 | checkpoint action head 兼容性；不得未验证复用其他机器人 norm stats |
| 新增 `examples/wheeled_bimanual/convert_data_to_lerobot.py` | 轨迹 → 三路图像 + 20 维 state/action + task + sidecar | 时钟不同步、坐标系与单位错误 |
| 新增 `examples/wheeled_bimanual/main.py` | 仿真观察 → WebSocket infer → 安全裁剪 → env step → 逐步 JSONL | 网络延迟、action chunk 陈旧、异常 episode 漏计 |
| 修改 `scripts/serve_policy.py` | 可选新增 `EnvMode.WHEELED_BIMANUAL`，或只用显式 checkpoint 模式 | 默认 checkpoint 不存在时不得伪造路径 |
| 新增 policy/config 单测 | 随机输入验证 shape、dtype、mask、输出截断、差分底盘 `vy=0` | 只看 shape 的测试发现不了单位与坐标错误 |

推理请求字段：`observation/base_image`、`observation/left_wrist_image`、`observation/right_wrist_image`、`observation/state: float32[20]`、`prompt`（当前子目标语言）。响应：`actions: float32[horizon, 20]`。`action_dim=32` 的 padding 只存在于模型内部，**不发送给仿真器**。

### 5.2 必须由外部模块承担

1. **任务规划器**：高层语言 + 对象/房间状态 + 技能库 + 失败历史 → 有序 subgoal、技能参数、前置/完成谓词。可为规则 / PDDL-TAMP / LLM-VLM planner；**MVP 必须有确定性非 VLA 版本**。
2. **执行监控器**：仿真状态 + BDDL 谓词 + 当前 subgoal + 超时 → `RUNNING/SUCCEEDED/FAILED/UNSAFE` 与证据。**不得仅依赖 VLA 自报成功**。
3. **仿真适配器**：机器人资产、控制器、底盘运动学、关节单位、相机、碰撞与 env step；统一 `reset/observe/step/evaluate_literals` 合约（具体 API 待版本确认）。
4. **安全过滤器**：速度/加速度/关节范围、夹爪范围、碰撞预检、禁入区、超时、emergency stop。**必须在动作进入仿真器之前执行**。
5. **感知与记忆**：房间图、对象身份、容器开闭、最后观测位置与不确定性。MVP 可用仿真真值取上界，正式泛化评测必须区分真值与感知估计。
6. **BDDL / Q-score 评测器**：必须调用目标基准的 canonical predicate evaluator；官方公式未核实前只实现并上报明确命名的 `LPC`。
7. **世界模型/MPC、RL 自改进**：作为 planner 候选排序器或离线数据选择器接入，不为此改动 openpi 的 WebSocket 基本契约。

---

## 6. 风险与回退路径

| 风险 | 失效方式 | 监测 | 回退 |
|---|---|---|---|
| 指标口径污染 | max-over-time literal、删崩溃 episode、换 seed、用自定义成功替代 canonical evaluator | manifest/hash 审计；排程 episode 数与结果行数核对 | 冻结 evaluator；崩溃计失败；官方 Q-score 未确认时退回 `LPC` |
| padding 冲突 | 20→32 的 padding 被当真实关节训练、归一化或发送到环境 | 单测检查后 12 维恒零、输出只取前 20 维 | 保持 `action_dim=32`，适配层统一截断；必要时为 FAST 另立 20 维配置并重验 checkpoint 兼容性 |
| DeltaActions 语义错位 | state 是底盘位姿而 action 是速度，或关节顺序不一致 | 逐索引单测 + 人工阶跃检查 | 底盘槽固定速度语义；全局位姿移到 monitor；不确定时先全 absolute 基线 |
| cross-embodiment gap | 固定底座预训练无法控制移动双臂；底盘运动致视觉分布漂移 | B0/B1/B2 分层对比；分报导航/左臂/右臂/协同 | 先非 VLA 导航 + VLA 静止底盘操作，再逐步加入底盘动作与双臂协同 |
| 长程误差累积 | 小定位/抓取误差使后续 subgoal 全败 | subgoal 曲线、首次失败位置、恢复次数 | 缩短 action chunk；每 subgoal 后重新观测；启用重试/回退/重规划 |
| 高层真值泄漏 | planner 用仿真真值却被当感知系统成绩 | 日志标记 `oracle` / `perception` | oracle 只作上界；正式结果切感知状态并单独报告 |
| 仿真器选择偏差 | 在 LIBERO 或抽象环境成功被解释为轮式双臂成功 | 报告强制记录 embodiment 与 simulator | LIBERO 只作链路测试；H 的结论只接受目标形态资产上的结果 |
| 资产/控制频率不一致 | 同策略在不同频率、单位、控制器上结果失真 | 记录 Hz、单位、控制模式、动作缩放、延迟 | 固定 canonical SI 单位；适配器负责转换；不同控制器分开建榜 |
| 恢复机制刷分 | 无限重试抬高成功率 | 固定最大重试、重规划与总 step budget | 同时报无恢复与固定恢复预算两组；超预算计失败 |
| 自改进数据泄漏 | 用评测失败轨迹训练后仍报同实例泛化 | 数据 lineage 与 scene/task hash 审计 | 评测实例永久隔离；自改进只用 train/dev，再在未见测试集评估 |
| 目标栈装不上 | Isaac/GPU/许可证/资产阻塞 | preflight + 最小 reset/step 测试 | CPU 合约模拟器 → LIBERO 链路 → 操作/导航卫星栈；**不伪造终局 H 结论** |

---

## 7. 下一步门槛

本计划获批后，按序推进且每一步都要可回退：

1. 冻结 `wheeled_bimanual_v0` schema 与 `household_long_v0` manifest（含 hash）。
2. 实现 CPU 合约模拟器 + 确定性 B0 规划器 + 执行监控器 + 固定评测器，在无 GPU 条件下跑通闭环与日志。
3. 在 GPU 主机上初始化 submodule、安装依赖、用合法本地 checkpoint 跑 LIBERO 链路冒烟。
4. 确认目标仿真器版本与轮式双臂资产后，接入 B1/B2，首次上报 LPC / E2E / SGSR。
5. 只有第 4 步完成才允许在 `rsi/leaderboard.md` 写入正式成绩。
