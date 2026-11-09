# leaderboards/log.md · 追加式实验登记
# 维护人：suyunhuan　最近更新：2026-11-09（首次创建）

只追加，不重写历史行。`status` 取值：`blocked`（未跑成）/ `dry-run`（仅环境与配置校验）/ `measured`（按固定口径实测）。
只有 `measured` 行才允许同步进 `rsi/leaderboard.md`。

| 日期 | slug | 形态 / 场景 | status | 主指标 | 实测值 | 口径 | 报告 |
|---|---|---|---|---|---|---|---|
| 2026-11-09 | wheeled-bimanual-household-minloop | 轮式底盘+升降躯干+双 7-DoF 臂 / 家庭长程 | `dry-run` | LPC + 端到端成功率 + SGSR | **无**（未跑仿真） | `household_long_v0` 未冻结；无 GPU、无仿真器、无本地 checkpoint | [report](../reports/2026-11-09-wheeled-bimanual-household-minloop.md) |

## 2026-11-09 · wheeled-bimanual-household-minloop

- 执行内容：只读规划 + `scripts/rsi/wheeled_bimanual_preflight.py` dry-run。
  首次运行（本次登记位补齐前）22 项检查 = 9 PASS / 12 BLOCKED / 1 INFO / 0 FAIL；
  补齐 plan 与 leaderboard 后 = 12 PASS / 9 BLOCKED / 1 INFO / 0 FAIL，剩余阻塞全部为 GPU / 依赖 / 仿真器类。
- 已校验：`wheeled_bimanual_v0` 20 维布局无重叠无空洞、`make_bool_mask(-3,8,-1,7,-1)` 与逐字段 delta/absolute 声明一致、
  20 维可装入 `action_dim=32`、三路图像槽位名与 `src/openpi/policies/libero_policy.py` 一致、
  参照 config（`pi05_libero` / `pi0_aloha` / `pi05_droid`）确实注册在 `src/openpi/training/config.py`。
- 未执行：任何仿真 rollout、任何训练、任何权重下载、任何真机动作。
- 阻塞主因：无 GPU；未选定仿真器且全部未安装；`third_party/{libero,aloha}` submodule 未 checkout；无 uv 与 openpi 依赖；
  `household_long_v0` manifest 未冻结；官方 Q-score 定义未核实。
