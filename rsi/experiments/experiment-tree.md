# experiment-tree.md · 实验树与经验沉淀
# 维护人：suyunhuan　最近更新：2026-11-09（登记 wheeled-bimanual-household-minloop dry-run）

## 实验四元组（假设 / 改动 / 指标 / 失败原因）

| 日期 | 假设 | 改动 | 指标（端到端 / subgoal） | 失败原因或结论 |
|---|---|---|---|---|
| 2026-11-09 | 轮式底盘+升降躯干+双 7-DoF 臂形态上，分层闭环（规划器 + openpi 子目标技能 + 执行监控）优于端到端单指令 VLA；固定底座预训练存在可量化 cross-embodiment gap | 仅文档与脚本级：plan 草案、`wheeled_bimanual_v0` 20 维 schema（JSON）、纯标准库 dry-run 校验器 `scripts/rsi/wheeled_bimanual_preflight.py`、leaderboard 骨架。openpi 代码零改动 | LPC（终止状态 BDDL literal 部分学分）+ 端到端成功率 + subgoal 成功率（micro/macro + 逐位置 SG1…SG15）。**本轮全部未测量** | 未进入实验阶段即被环境阻塞：无 GPU、仿真器未选定且全部未安装、轮式双臂资产未核实、无已批准 plan、无本地 checkpoint。已验证结论仅限「schema 与 openpi 现有动作/图像契约机械一致」，不含任何性能声明。[报告](../reports/2026-11-09-wheeled-bimanual-household-minloop.md) |

## 经验区（一次性记录；长期规则回写 `.cursor/rules/rsi-core.mdc`）

- （暂无）
