# keywords.md · 关键词与业务方向库
# 维护人：suyunhuan　最近更新：2026-11-09（新增 R9 B1K 词组与 6 条热度信号；由 C2 keyword-radar 常规更新）
# 注：2026-11-09 的增补来自 RSI 自迭代调度的「数据 × 形态」联合搜索，未改动下方「路线覆盖记录」矩阵（该表由 C2 维护）。
#     因此 R9 暂未出现在该矩阵中，请 C2 下次运行时补一行 R9。

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
- R9 B1K 评测主线 / 轮式双臂家庭闭环仿真（2026-11-09 新增，来自 RSI 自迭代调度的「数据 × 形态」联合搜索；与 R1-R8 交叉使用，不替代任何现有分组）
  - 基准与指标：BEHAVIOR-1K, B1K, BEHAVIOR Challenge, OmniGibson, BDDL goal predicate, Q-score, partial success score,
    full-task success rate, hidden test instance, normalized simulation time, base distance, end-effector displacement
  - 形态与控制接口：Galaxea R1 Pro, r1pro, wheeled bimanual, holonomic base, articulated trunk, whole-body control,
    action space design, embodiment configuration, JointController, InverseKinematicsController, MultiFingerGripperController,
    receding horizon control, action horizon, replanning interval, absolute action parameterization
  - 数据配方：recovery demonstration, failed-grasp recovery, perturb-and-reconnect, motion-planner demonstration,
    rejection sampling fine-tuning (RFT), offline data flywheel, skill annotation segmentation, action space reprojection,
    IK consistency filtering, narrow demonstration manifold, task balancing vs reweighting
  - 失败模式与编排：gripper closed on air, execution-order confusion, premature termination, out-of-distribution freeze,
    search-heavy task, frontier exploration, open-vocabulary detection, proprioception-triggered completion check,
    motion planner / VLA interleaving, executable structure scaling, per-task policy routing

## 代码基座（开源；仅供 C3 / C4 方案设计与验证环节结合，检索环节不涉及）
- openpi（π0 / π0.5）：https://github.com/Physical-Intelligence/openpi（本仓库：https://github.com/suyunhuan/Physical-AI）
- 仿真评测：LIBERO、BEHAVIOR-1K / OmniGibson；数据生态：LeRobot

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
- executable structure scaling / hierarchical physical recursive self-improvement | 2026-11-09 | 来自 2026 BEHAVIOR Challenge 榜首方案（参赛方自建页面，技术报告在准备中，未经同行评议）；相关性高，证据强度待补 | 路线 R2 + R4
- motion planner / VLA interleaving（MPVI） | 2026-11-09 | arXiv 2606.00985v1，自述 50 任务 task progress +113% 且无需额外训练；相关性高 | 路线 R2 + R1
- failed-grasp recovery data / perturb-and-reconnect | 2026-11-09 | arXiv 2512.06951v2 失败模式分析（灵巧度约占失败 1/3；BEHAVIOR-1K 数据无恢复示范）；相关性高 | 路线 R5 + R8
- receding horizon control（对比 temporal ensemble / receding temporal） | 2026-11-09 | arXiv 2512.10071v2 消融（**单任务** `turning_on_radio`，样本面窄，需独立复核）；相关性高 | 路线 R1
- embodiment configuration as a search dimension（`--robot-config`，赛道不固定形态） | 2026-11-09 | behavior.stanford.edu/challenge/evaluation.html；相关性高 | 路线 R7
- rejection sampling fine-tuning 的长程崩塌（保留 episode 数与 episode 长度 Spearman ≈ −0.45） | 2026-11-09 | 第三方复现分析博客 bushuyeu.com，**可信度低于论文**；相关性中 | 路线 R4 + R5

## 降权 / 待移除（C2 标注：旧词 + 理由 + 日期）
- （例）yyy | 热度连续 2 周下降 | YYYY-MM-DD
