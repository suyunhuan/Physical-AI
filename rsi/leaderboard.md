# leaderboard.md · RSI 主榜
# 维护人：suyunhuan　最近更新：2026-11-09（首次创建；尚无任何成绩）

本文件是 RSI 实验成绩的唯一主榜。追加式明细写在 `rsi/leaderboards/log.md`。

## 硬规则

1. **没有实际跑过的实验不得入榜。** 未执行、被阻塞、仅文档级的工作只能登记在 `rsi/leaderboards/log.md` 并标 `status=blocked`。
2. **口径必须固定且可复现**：同一榜单内的所有行必须共用 suite、seed 集合、trial 数、超时、恢复预算与判定函数；任一项变化即另开榜单版本。
3. **长程任务必须同时报告端到端完成率与 subgoal 级成功率**（rsi-core 硬规则 8）；只报单步或只报端到端的结果不得入榜。
4. **指标命名不得冒用**：未核实官方定义的指标（如 BEHAVIOR 的 Q-score）一律用自定义明确名称（如 `LPC`）并在榜单脚注写出公式。
5. **崩溃、超时、安全终止一律计失败**，不得从分母剔除。
6. 劣化如实记录；禁止调参凑数与选择性报告。

## 榜单 · 轮式双臂家庭长程（`household_long_v0`）

口径：形态 = 轮式底盘 + 升降躯干 + 双 7-DoF 臂 + 双夹爪；10 个固定任务 × 10 个固定初始状态；
seed = `[7,17,27,37,47,57,67,77,87,97]`；每任务 5-15 个冻结有序 subgoal；**suite 尚未冻结，故本榜不接受任何成绩**。

| 排名 | 日期 | 方案 | 基线类型 | LPC（micro / macro） | 端到端成功率 | SGSR（micro / macro） | 仿真器 / 形态 | 恢复预算 | 报告 |
|---|---|---|---|---|---|---|---|---|---|
| — | 2026-11-09 | household-minloop | — | 未运行 | 未运行 | 未运行 | 未选定（无 GPU） | — | [report](reports/2026-11-09-wheeled-bimanual-household-minloop.md) |

脚注 · LPC 定义（终止状态计算，禁止 max-over-time）：

```text
LPC_e = |{ l ∈ G_e : canonical evaluator 在终止状态判定 l 为真 }| / |G_e|
```

## 榜单 · LIBERO（固定 suite）

口径：`examples/libero/main.py` 默认判定（环境 `done`），`num_trials_per_task=50`、`seed=7`、`replan_steps=5`。
该榜只能证明链路可用，**不能用于轮式双臂形态假设的结论**。

| 排名 | 日期 | 配置 | suite | 成功率 | subgoal 成功率 | 报告 |
|---|---|---|---|---|---|---|
| — | — | （尚无本仓库自测成绩） | — | — | — | — |

注：openpi 上游 `examples/libero/README.md` 报告的 π0.5 @30k 成绩属于**上游数据**，未在本仓库复现，不计入本榜。
