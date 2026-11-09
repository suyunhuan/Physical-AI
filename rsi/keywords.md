# keywords.md · 关键词与业务方向库
# 维护人：suyunhuan　最近更新：2026-11-09（榜单冲顶 / 数据×形态种子）

## 业务方向
- 具身智能长程家庭任务（Long-horizon Household Manipulation）
  - 移动操作（mobile manipulation）、桌面操作、多房间取物、收纳 / 清洁 / 厨房辅助
  - **榜单冲顶**：主攻 BEHAVIOR-1K（B1K）冲击 #1；数据与形态联合搜索；闭环仿真默认轮式双臂家庭场景
  - π/openpi 只是实验基座；研究范围开放，不限 VLA，允许符号规划、世界模型、RL、数据仿真、感知记忆、安全评测等路线

## 短期业务验证主线（C1 强相关论文的筛选基准）
1. 长程任务的子目标分解、规划与执行监控（hierarchical planning / TAMP / world model planning / subgoal / skill chaining / failure recovery）
2. 家庭场景的数据效率、泛化与可靠评测（少样本学习、跨物体跨任务跨场景泛化、sim2real、open-vocabulary、合成数据、闭环评测）
3. 榜单冲顶与数据×形态联合（B1K Q-score、示范数据配方、跨形态重定向、轮式双臂控制接口）

## 开放技术路线关键词组（C1/C2 必须跨组检索，不得只搜 VLA）
- R1 VLA/端到端：VLA, vision-language-action, pi0, pi0.5, openpi, diffusion policy, flow matching, action tokenization, behavior cloning, imitation learning
- R2 分层/符号规划：hierarchical planning, LLM planner, VLM planner, TAMP, task and motion planning, PDDL, skill library, skill chaining, subgoal decomposition
- R3 世界模型/MPC：world model, video world model, dynamics model, latent planning, model-based RL, MPC, model predictive control, counterfactual simulation
- R4 RL/自改进：offline RL, online RL, RL fine-tuning, preference optimization, self-play, self-improvement, curriculum learning, test-time scaling
- R5 数据/仿真：demonstration data, LeRobot, synthetic data, domain randomization, digital twin, sim2real, active learning, teleoperation, data engine, scene generation, MimicGen, data mixture
- R6 感知/记忆：3D scene graph, affordance, open-vocabulary perception, object-centric representation, spatial memory, episodic memory, tactile sensing, force feedback
- R7 基础模型/跨形态：robot foundation model, generalist policy, cross-embodiment, multi-task pretraining, mobile manipulation, dexterous manipulation, wheeled bimanual, dual-arm
- R8 安全/恢复/评测：constraint satisfaction, uncertainty estimation, safety guardrail, failure recovery, human intervention, closed-loop evaluation, long-horizon benchmark, success rate, Q-score, BDDL
- R9 榜单/挑战赛：BEHAVIOR-1K, BEHAVIOR Challenge, B1K, OmniGibson, RoboCasa, RoboCasa365, LIBERO (regression only), CALVIN, ManiSkill-HAB, Habitat rearrangement, leaderboard, held-out test

## 代码基座（开源；仅供 C3 / C4 方案设计与验证环节结合，检索环节不涉及）
- openpi（π0 / π0.5）：https://github.com/Physical-Intelligence/openpi（本仓库：https://github.com/suyunhuan/Physical-AI）
- 冲顶评测：B1K / BEHAVIOR Challenge；卫星：RoboCasa；回归：LIBERO；数据生态：LeRobot / 官方 teleop

## 核心关键词（长期稳定，读论文与检索的基座）
embodied AI, long-horizon household task, household manipulation, mobile manipulation,
long-horizon planning, subgoal decomposition, generalization, sim2real, closed-loop evaluation,
world model, TAMP, MPC, RL, VLA, multimodal, 3D scene graph, affordance, safety, failure recovery,
BEHAVIOR-1K, Q-score, wheeled dual-arm, bimanual, data engine, cross-embodiment, leaderboard

## 路线覆盖记录（由 C2 / 榜单雷达更新；无命中写“未覆盖”）
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
| R9 榜单/挑战赛 | 未初始化 | — | — | 首次榜单雷达后填写 |

## 热度信号关键词（C2 / 榜单雷达增补：新词 + 日期 + 来源热度）
- BEHAVIOR-1K / B1K Challenge | 2026-11-09 | 种子：主冲顶榜，Q-score 口径，相关性高
- RoboCasa365 leaderboard | 2026-11-09 | 种子：卫星厨房多任务榜，相关性高
- wheeled bimanual household sim | 2026-11-09 | 种子：默认闭环形态，相关性高
- data×embodiment joint search | 2026-11-09 | 种子：一等杠杆，相关性高

## 降权 / 待移除（C2 标注：旧词 + 理由 + 日期）
- （例）yyy | 热度连续 2 周下降 | YYYY-MM-DD
