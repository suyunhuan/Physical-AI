# 榜单冲顶阶段 · 入口说明
# 维护人：suyunhuan　最近更新：2026-11-09

## 北极星
在公开具身榜单冲击 **#1**。主榜：**BEHAVIOR-1K / BEHAVIOR Challenge（B1K）**。

## 主榜与卫星
| 类型 | 名称 | 主指标 | 备注 |
|---|---|---|---|
| 主榜 | B1K / BEHAVIOR Challenge | Q-score + 全任务成功率 | https://behavior.stanford.edu/challenge/ |
| 卫星 | RoboCasa / RoboCasa365 | Overall / 分 split 成功率 | 厨房多任务、跨形态 |
| 回归 | LIBERO 固定 suite | suite 成功率 | **仅** openpi 回归，禁止冒充主榜 |

## 数据 × 形态
实验假设必须为 `H=(任务切片, 形态配置, 数据配方, 评测口径)`。  
闭环仿真默认：**轮式底盘 + 双臂** 家庭长程场景。

## 日志与计划
- 榜位与 H 日志：`rsi/leaderboards/log.md`
- 日报式榜单快照：`rsi/leaderboards/YYYY-MM-DD-board.md`
- 联合搜索方案：`rsi/plans/YYYY-MM-DD-data-embodiment.md`

## Automations
- 新建草稿：`.cursor/automations/leaderboard-radar-automation.md` 等 3 条
- 粘贴包（Project store）：见协调文档 `leaderboard-automation-paste-packs.md`
- 默认不拉权重、不开训、不部署真机

## 相关设计
Project store：`/cursor/stores/self/docs/leaderboard-rsi-design.md`
