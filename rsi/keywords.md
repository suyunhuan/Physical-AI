# keywords.md · 关键词与业务方向库
# 维护人：suyunhuan　最近更新：2026-11-09（由 C2 keyword-radar 更新）

## 业务方向
- 具身智能长程家庭任务（Long-horizon Household Manipulation）
  - 移动操作（mobile manipulation）、桌面操作、多房间取物、收纳 / 清洁 / 厨房辅助
  - π/openpi 只是实验基座；研究范围开放，不限 VLA，允许符号规划、世界模型、RL、数据仿真、感知记忆、安全评测等路线

## 短期业务验证主线（C1 强相关论文的筛选基准）
1. 长程任务的子目标分解、规划与执行监控（hierarchical planning / TAMP / world model planning / subgoal / skill chaining / failure recovery / agent harness / preview-execute-verify / prediction-regulated memory）
2. 家庭场景的数据效率、泛化与可靠评测（少样本学习、跨物体跨任务跨场景泛化、reasoning-aligned fine-tuning、sim2real、open-vocabulary、手持夹爪/人类视频规模化数据、合成数据、behavior-conditioned 闭环评测）

## 开放技术路线关键词组（C1/C2 必须跨组检索，不得只搜 VLA）
- R1 VLA/端到端：VLA, vision-language-action, pi0, pi0.5, openpi, diffusion policy, flow matching, action tokenization, behavior cloning, imitation learning, reasoning-aligned fine-tuning (RAFT), encoder-free VLA, sparse MoE action expert
- R2 分层/符号规划：hierarchical planning, LLM planner, VLM planner, TAMP, task and motion planning, PDDL, skill library, skill chaining, subgoal decomposition, agent harness, explicit task belief, interactive autosteer, inline subtask generation
- R3 世界模型/MPC：world model, video world model, world-action model (WAM), dynamics model, latent planning, model-based RL, MPC, model predictive control, counterfactual simulation, action-conditioned multiview simulator, training-time future prediction (La-JEPA)
- R4 RL/自改进：offline RL, online RL, RL fine-tuning, preference optimization, proactive human-in-the-loop (PHIL), zero-shot VLM reward model (D&A), graph-search failure recovery, self-play, self-improvement, curriculum learning, test-time scaling
- R5 数据/仿真：demonstration data, LeRobot, LanceDB streaming, synthetic data, domain randomization, digital twin, sim2real, active learning, teleoperation, in-the-wild handheld data collection (UMI-Live / YUBI), egocentric human video scaling, data engine, scene generation
- R6 感知/记忆：3D scene graph, affordance, open-vocabulary perception, object-centric representation, spatial memory, episodic memory, environment and process memory, prediction-regulated memory (PREM), tactile sensing, tactile foundation model (TFM), force feedback
- R7 基础模型/跨形态：robot foundation model, generalist policy, cross-embodiment, multi-task pretraining, mobile manipulation, unified navigation-manipulation WAM, environment-aware retargeting, dexterous manipulation
- R8 安全/恢复/评测：constraint satisfaction, uncertainty estimation, safety guardrail, admission gateway, preview-execute-verify loop, failure recovery, human intervention, closed-loop evaluation, behavior-conditioned evaluation, distributed in-the-wild evaluation (RoboColosseum), long-horizon benchmark, success rate

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
| R1 VLA/端到端 | 6 | `RAFT` (arXiv:2611.04368)、`NEO-VLA` (arXiv:2611.06918)、`LingBot-VLA 2.0`、`G0.5`、`Wall-OSS-0.5` | 2026-11-09 | 覆盖充分；关注两阶段推理对齐微调（RAFT）与内联子任务生成 |
| R2 分层/符号规划 | 4 | `Auriga` (arXiv:2611.01112)、`LeRobot v0.7.0 (/subtask & /autosteer)`、`FineART-VLA`、`Xiaomi-Robotics-1 Agent` | 2026-11-09 | 本周集中于 Agent Harness 与 VLM 在线子目标分解；传统符号 TAMP/PDDL 在 11.02–11.09 无新 arXiv 论文，下次专项补检 `PDDLStream`、`symbolic TAMP`、`bilevel planning` |
| R3 世界模型/MPC | 6 | `PrimeSim` (arXiv:2611.04870)、`NVIDIA Cosmos 3` (arXiv:2611.06627)、`La-JEPA` (arXiv:2611.08156)、`Fysiverse-UniWAM`、`Mundo`、`AGIBOT GO-3 (WRAM)` | 2026-11-09 | 动作条件世界模型（WAM）与神经仿真器密集爆发；显式在线 MPC/轨迹优化较少，下次专项补检 `latent MPC`、`contact-implicit MPC` |
| R4 RL/自改进 | 5 | `PHIL` (arXiv:2611.05667)、`D&A` (arXiv:2611.03622)、`PrimeSim GRPO` (arXiv:2611.04870)、`GR-BC` (CoRL 2026)、`RSI-Nav` | 2026-11-09 | 主动偏好学习、零样本 VLM 奖励模型与世界模型内 GRPO 覆盖良好；下次补检 `reset-free real-world RL`、`autonomous skill discovery` |
| R5 数据/仿真 | 7 | `LeRobot v0.7.0` (300TB + LanceDB)、`AIRoA-0` (arXiv:2611.03815)、`Open-HumanWAM-50K` (arXiv:2611.06817)、`UMI-Live` (arXiv:2610.39385)、`ToyBlocks`、`HIW-500`、`Rollout then Recycle` (arXiv:2611.03168) | 2026-11-09 | 覆盖极强，手持夹爪采数、5 万小时人类第一视角视频与真实家庭数据集均已覆盖 |
| R6 感知/记忆 | 5 | `PREM` (arXiv:2611.00634)、`RoboCasa-Mem` (arXiv:2611.06475)、`TacMind` (arXiv:2611.00455)、`Evaluating TFMs` (arXiv:2611.00957)、`Mundo` | 2026-11-09 | 循环视觉记忆（PREM）、环境/过程记忆与触觉基础模型覆盖充分；显式开放词汇 3D 场景图本周较少，下次补检 `3D scene graph manipulation`、`functional affordance grounding` |
| R7 基础模型/跨形态 | 6 | `CMU Pixel & Pixel-UMI` (arXiv:2611.03648 / 2611.03647)、`AGIBOT GO-3 Preview`、`AIRoA-0` (arXiv:2611.03815)、`LingBot-VLA 2.0`、`Fysiverse-UniWAM` | 2026-11-09 | 跨本体统一动作空间、轮式双臂全身协同与导航—操作统一建模覆盖充分 |
| R8 安全/恢复/评测 | 6 | `RoboColosseum` (arXiv:2611.02497)、`Auriga` (arXiv:2611.01112)、`PHIL` (arXiv:2611.05667)、`Rollout then Recycle` (arXiv:2611.03168)、`RoboCasa-Mem` (arXiv:2611.06475)、`Worken` | 2026-11-09 | 分布式真机评测、准入网关轨迹预览恢复、主动纠偏与行为条件评测覆盖全面 |

## 热度信号关键词（C2 每日增补：新词 + 日期 + 来源 + 相关性 + 技术路线）
- `agent harness` / `preview-execute-verify loop` | 2026-11-09 | 来源：arXiv:2611.01112 (Auriga)，RoboDojo & RoboCasa365 榜首，热度高 | 相关性：高（通过显式任务信念与单入口准入网关执行前轨迹预览、容差监控与单回合原位恢复，闭合 68.3% 规划—执行鸿沟） | 技术路线：R2 分层/符号规划 · R8 安全/恢复/评测
- `world-action model (WAM)` / `action-conditioned multiview simulator` | 2026-11-09 | 来源：arXiv:2611.04870 (PrimeSim)、arXiv:2611.06627 (NVIDIA Cosmos 3)、LeRobot v0.7.0，热度极高 | 相关性：高（支持 105 秒长程多视角动作条件仿真与未来状态预测，与 LIBERO 物理评测相关性 r=0.99，支撑闭环评测与 GRPO 优化） | 技术路线：R3 世界模型/MPC · R5 数据/仿真
- `training-time future prediction` (`La-JEPA`) | 2026-11-09 | 来源：arXiv:2611.08156 (La-JEPA)，Paper Daily W45 具身周榜 Top 2，热度高 | 相关性：高（在 V-JEPA 2.1 隐空间训练期联合预测未来特征塑造表征、推理期跳过未来生成仅解码动作，推理速度达 Fast-WAM 2.6 倍且真机长程媲美 π0.5） | 技术路线：R3 世界模型/MPC · R1 VLA/端到端
- `prediction-regulated memory (PREM)` | 2026-11-09 | 来源：arXiv:2611.00634 (PREM)，上海交大，热度高 | 相关性：高（利用预测—观测空间残差门控循环视觉记忆更新，在 π0.5 上仅增 7.7ms 延迟，将 RMBench M(1) 记忆依赖操作成功率从 14.4% 提至 83.8%） | 技术路线：R6 感知/记忆 · R3 世界模型/MPC
- `environment and process memory` / `behavior-conditioned evaluation` | 2026-11-09 | 来源：arXiv:2611.06475 (RoboCasa-Mem)，USTC 等，热度中高 | 相关性：高（解耦长程移动操作中的空间环境记忆与任务进度记忆，并依据机器人早期行为动态约束后续步骤评测） | 技术路线：R6 感知/记忆 · R8 安全/恢复/评测
- `reasoning-aligned fine-tuning (RAFT)` | 2026-11-09 | 来源：arXiv:2611.04368 (RAFT)，Princeton & MSR，Paper Daily W45 Top 3，热度高 | 相关性：高（先在空间/物体推理标注上训练并冻结 LoRA 再微调动作，DROID 真机 OOD 成功率从 27.9% 跃升至 75.0%） | 技术路线：R1 VLA/端到端 · R2 分层/符号规划
- `proactive human-in-the-loop (PHIL)` | 2026-11-09 | 来源：arXiv:2611.05667 (PHIL)，KIT，Paper Daily W45 Top 10，热度高 | 相关性：高（通过 XR 预览未来动作块在错误发生前主动接管，构造同状态被拒预测 vs 纠正动作偏好对，减少 10 倍冗余恢复动作） | 技术路线：R4 RL/自改进 · R8 安全/恢复/评测
- `decoupled description and assessment (D&A)` | 2026-11-09 | 来源：arXiv:2611.03622 (D&A)，UW & NVIDIA，热度中高 | 相关性：高（将零样本 VLM 奖励评估解耦为客观动态描述与量表打分，消除确认偏差，提供家庭长程子目标稠密奖励信号） | 技术路线：R4 RL/自改进 · R8 安全/恢复/评测
- `in-the-wild handheld data collection` (`YUBI` / `UMI-Live`) | 2026-11-09 | 来源：arXiv:2611.03815 (AIRoA-0，W45 Top 1)、arXiv:2610.39385 (UMI-Live，W45 Top 8)，热度极高 | 相关性：高（仅靠手持夹爪在自然环境中采集双手演示，零真机遥操作数据实现 78% 跨本体长程家务成功率，π0.5 微调 10/10 成功） | 技术路线：R5 数据/仿真 · R7 基础模型/跨形态
- `distributed in-the-wild evaluation` (`RoboColosseum`) | 2026-11-09 | 来源：arXiv:2611.02497 (RoboColosseum)，NUS/UW/Stanford/Ai2/HF，124 场地 5,699 次真机对比，热度高 | 相关性：高（确立跨本体多场地真实闭环评测与部分进度度量，揭示零样本排名与微调后排名反转现象） | 技术路线：R8 安全/恢复/评测 · R7 基础模型/跨形态
- `interactive autosteer` / `language-in-the-loop rollout` | 2026-11-09 | 来源：Hugging Face LeRobot v0.7.0 Release，GitHub 28.7k+ Stars，热度极高 | 相关性：高（支持策略运行中实时接收 `/subtask`、`/vqa`、`/autosteer` 指令切换子目标或自主巡航） | 技术路线：R2 分层/符号规划 · R5 数据/仿真

## 降权 / 待移除（C2 标注：旧词 + 理由 + 日期 + 技术路线；保留历史不直接删除）
- `pure action-free video world model`（无动作条件纯视频生成世界模型） | 历史理由：2026-11 行业与学术信号（量子位《资本正在撤离“世界模型”》、PrimeSim arXiv:2611.04870、La-JEPA arXiv:2611.08156）证实，缺乏精确动作条件对齐与物理约束的纯像素视频生成模型在长程操作中误差累积严重、推理开销过高，研究重心已转入动作条件世界模型（WAM）与隐空间未来特征预测 | 2026-11-09 | 技术路线：R3 世界模型/MPC
- `reactive-only post-error takeover`（纯事后被动接管数据聚合） | 历史理由：arXiv:2611.05667 (PHIL) 实证表明，待错误发生后再接管会将大量补救动作混入训练集，导致策略在正常执行中也产生约 10 倍非必要恢复行为；后续优先检索主动预览接管（proactive intervention）与同状态偏好学习 | 2026-11-09 | 技术路线：R4 RL/自改进 · R8 安全/恢复/评测

