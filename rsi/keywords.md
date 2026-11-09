# keywords.md · 关键词与业务方向库
# 维护人：suyunhuan　最近更新：2026-11-09（榜单雷达增量；初始种子由 C2 keyword-radar 建立）

## 业务方向
- 具身智能长程家庭任务（Long-horizon Household Manipulation）
  - 移动操作（mobile manipulation）、桌面操作、多房间取物、收纳 / 清洁 / 厨房辅助
  - π/openpi 只是实验基座；研究范围开放，不限 VLA，允许符号规划、世界模型、RL、数据仿真、感知记忆、安全评测等路线

## 短期业务验证主线（C1 强相关论文的筛选基准）
1. 长程任务的子目标分解、规划与执行监控（hierarchical planning / TAMP / world model planning / subgoal / skill chaining / failure recovery）
2. 家庭场景的数据效率、泛化与可靠评测（少样本学习、跨物体跨任务跨场景泛化、sim2real、open-vocabulary、合成数据、闭环评测）

## 开放技术路线关键词组（C1/C2 必须跨组检索，不得只搜 VLA）
- R1 VLA/端到端：VLA, vision-language-action, pi0, pi0.5, openpi, diffusion policy, flow matching, action tokenization, behavior cloning, imitation learning
- R2 分层/符号规划：hierarchical planning, LLM planner, VLM planner, TAMP, task and motion planning, PDDL, skill library, skill chaining, subgoal decomposition
- R3 世界模型/MPC：world model, video world model, dynamics model, latent planning, model-based RL, MPC, model predictive control, counterfactual simulation
- R4 RL/自改进：offline RL, online RL, RL fine-tuning, preference optimization, self-play, self-improvement, curriculum learning, test-time scaling
- R5 数据/仿真：demonstration data, LeRobot, synthetic data, domain randomization, digital twin, sim2real, active learning, teleoperation, data engine, scene generation
- R6 感知/记忆：3D scene graph, affordance, open-vocabulary perception, object-centric representation, spatial memory, episodic memory, tactile sensing, force feedback
- R7 基础模型/跨形态：robot foundation model, generalist policy, cross-embodiment, multi-task pretraining, mobile manipulation, dexterous manipulation
- R8 安全/恢复/评测：constraint satisfaction, uncertainty estimation, safety guardrail, failure recovery, human intervention, closed-loop evaluation, long-horizon benchmark, success rate

## 代码基座（开源；仅供 C3 / C4 方案设计与验证环节结合，检索环节不涉及）
- openpi（π0 / π0.5）：https://github.com/Physical-Intelligence/openpi（本仓库：https://github.com/suyunhuan/Physical-AI）
- 仿真评测：LIBERO；数据生态：LeRobot

## 核心关键词（长期稳定，读论文与检索的基座）
embodied AI, long-horizon household task, household manipulation, mobile manipulation,
long-horizon planning, subgoal decomposition, generalization, sim2real, closed-loop evaluation,
world model, TAMP, MPC, RL, VLA, multimodal, 3D scene graph, affordance, safety, failure recovery

## 路线覆盖记录（由 C2 每次更新；无命中写“未覆盖”，不要写 0 代表没有研究）
| 路线 | 本次候选数 | 代表论文/信号 | 最近覆盖日期 | 补检建议 |
|---|---|---|---|---|
| R1 VLA/端到端 | 未初始化 | — | — | 首次雷达扫描后填写 |
| R2 分层/符号规划 | 未初始化 | — | — | 首次雷达扫描后填写 |
| R3 世界模型/MPC | 未初始化 | — | — | 首次雷达扫描后填写 |
| R4 RL/自改进 | 未初始化 | — | — | 首次雷达扫描后填写 |
| R5 数据/仿真 | 未初始化 | — | — | 首次雷达扫描后填写 |
| R6 感知/记忆 | 未初始化 | — | — | 首次雷达扫描后填写 |
| R7 基础模型/跨形态 | 未初始化 | — | — | 首次雷达扫描后填写 |
| R8 安全/恢复/评测 | 未初始化 | — | — | 首次雷达扫描后填写 |

## 热度信号关键词（C2 每日增补：新词 + 日期 + 来源热度）
- （例）xxx 概念 | YYYY-MM-DD | 来自 GitHub Trending / HF 趋势榜，热度高，相关性中

### 榜单雷达增量 · 2026-11-09（来源：B1K 2026 官方榜单 + RoboCasa365 榜单；详见 rsi/leaderboards/2026-11-09-board.md）
榜单侧读数：B1K 与 RoboCasa365 的榜首均为「智能体 / 可执行结构」类系统而非单体 VLA，WAM 占两榜第 2 梯队，π0.5 微调退为基线带。以下词按此优先级排列。

- world action model, WAM | 2026-11-09 | B1K verified #2 IF1001「VLA WAM」0.6155、#3 Cyber「WAM」0.5955；RoboCasa365 #2/#4 Awomo-0.5I/0.5V；热度高，相关性高（R3+R1）
- video-action co-training / joint video-action prediction | 2026-11-09 | WAM 族定义（视频生成底座联合预测未来视频与动作）；热度高，相关性高（R3）
- recursive self-improvement, RSI / hierarchical physical RSI | 2026-11-09 | B1K verified #1 The North Star「HiPhys-RSI」0.6828；#6 XYRobot「VLA+RSI」；热度高，相关性高（R4+R2）
- executable structure / executable procedure / tool composition | 2026-11-09 | HiPhys-RSI 自述：改进全部沉淀为可执行 procedure 与 tool，而非模型权重；热度高，相关性高（R2+R4）
- VLM coding agent / code as policy / code as scaling interface | 2026-11-09 | HiPhys-RSI（冻结 VLM coding agent 读反馈改写代码）；B1K 自报条目 `huawei-ai-algorithm-dept-gpt6-code-as-policy` 0.4076；A²MEAS 论文 arXiv:2611.09124；热度高，相关性高（R2）
- per-task routing / policy-pipeline routing | 2026-11-09 | HiPhys-RSI 推理期按任务路由到 pipeline 或 VLA 策略；热度中，相关性高（R2+R8）
- agentic embodied intelligence / embodied multi-agent framework | 2026-11-09 | arXiv:2611.09124（2026-11-06）；RoboCasa365 新增 `[AGENTIC]` 条目类型（HexaShell 1.5，85.6）；热度高，相关性高（R2+R7）
- correction code / corrective supervision / residual correction adapter | 2026-11-09 | A²MEAS：把纠正语言+落地空间证据+执行历史+动作提案编码为条件表示，经残差 adapter 调制 action expert 隐状态，权重全冻结；热度中，相关性高（R8+R1）
- diagnostic agent / grounded failure diagnosis | 2026-11-09 | A²MEAS MetaBrain + 诊断 agent（定位/分割/跟踪/深度/机器人状态）；热度中，相关性高（R6+R8）
- motion-aware history conditioning | 2026-11-09 | A²-WLA 动作模型组件（视觉历史 + 预测场景特征）；热度中，相关性高（R1+R3）
- BDDL partial credit / Q-score | 2026-11-09 | B1K 2026 主排名指标定义（满足的 goal predicate 占比，100 任务平均）；热度中，相关性高（R8）—— 固定评测口径用词
- subgoal-level progress score / task progress | 2026-11-09 | B1K Q-score 与 SERF（arXiv:2606.12956）均以 subgoal 完成占比计分；对应 rsi-core 硬规则 8；热度中，相关性高（R8）
- composite-unseen generalization / task composition generalization | 2026-11-09 | RoboCasa365 三 split 断崖：π0.5 39.6%→7.1%→1.2%，最强 Agent 91.1%→85.0%→80.0%；热度高，相关性高（R7+R8）
- evaluation noise floor / paired evaluation / run-to-run variance | 2026-11-09 | arXiv:2610.37917 同策略重跑 ΔQ +0.014±0.021，95% CI [−0.027,+0.056] → ±0.06 内不可区分；热度中，相关性高（R8）
- search-heavy task / occlusion search / time-budget exhaustion | 2026-11-09 | HiPhys-RSI 自述 hidden 集最大跌幅来源；B1K 规则：超预算 rollout 计 0 分；热度中，相关性高（R6+R8）
- snapshot restart / failed-episode restart | 2026-11-09 | arXiv:2610.37917 数据采集消融：省 29–43% 仿真步且不降成功率；热度中，相关性高（R5）
- stage belief / task stage token / voted stage | 2026-11-09 | 2025 冠军改装项，被 2026 复现沿用；快照重启不恢复 stage belief 则 ΔQ −0.053 / ΔSR −5.1pp；热度中，相关性高（R2+R5）
- advantage labeling / RECAP-style advantage guidance | 2026-11-09 | 第三方 π0.5 复现的 Phase 2 配方（advantage 标注随 RECAP / π*0.6）；消融显示强度 >1 边缘有害；热度中，相关性高（R4）
- rollout-demonstration mixture / success-rate-weighted data budget | 2026-11-09 | 公开配方：逐任务 rollout 占比 3%–55%（中位 42%），全局 36% 帧来自 rollout，旧 wave 半衰期 ~21k 步；热度中，相关性高（R5）
- demonstration-length-aware task sampling | 2026-11-09 | 示范长度 12 倍差，按总长 0.35 次幂加权压到 2.4 倍；热度低，相关性高（R5）
- action-chunk execution horizon / overlap inpainting / playback speed-up | 2026-11-09 | arXiv:2610.37917 推理消融：horizon 26→13 即 ΔQ −0.165；1.3× 加速应保留；overlap inpainting 关闭 n.s.；去噪 20→1 步 n.s.；热度中，相关性高（R1）
- gripper snap / release-threshold projection | 2026-11-09 | OmniGibson 仅在夹爪指令恰为 1.0 时释放物体，>0.9 投影到 1.0；关闭后 ΔSR −5.3pp；热度低，相关性高（R1+R8）
- spatiotemporal feature map / neural point map conditioning | 2026-11-09 | SERF（arXiv:2606.12956）：环境与关节机器人同潜空间 neural points，在线更新后作 VLA 状态输入；3 个 B1K 任务进度 44.0%→58.7%，未访问区域 28.0%→51.0%；热度中，相关性高（R6）
- free embodiment choice / custom robot config（跨形态设计自由度） | 2026-11-09 | B1K 2026 取消固定本体，可提交任意 OmniGibson 支持机器人；但 Top-6 无条目公开声明换本体（未核实）→ 未被利用的自由度；热度低，相关性高（R7）
- websocket policy server / action-chunk replay protocol | 2026-11-09 | B1K 官方 evaluator（`omnigibson.eval.eval`，协议改编自 openpi）；chunk replay 需首动作与 chunk[0] 严格相等，禁用于时序集成；热度低，相关性中（R8）
- GR00T N1.7 | 2026-11-09 | B1K 2026 第二基线（与 π0.5 并列）；自报分区该基线微调条目 Q 0.0；热度中，相关性中（R1+R7）

## 降权 / 待移除（C2 标注：旧词 + 理由 + 日期）
- （例）yyy | 热度连续 2 周下降 | YYYY-MM-DD
