# experiment-tree.md · 实验树与经验沉淀
# 维护人：suyunhuan　最近更新：2026-11-09

## 实验四元组（假设 / 改动 / 指标 / 失败原因）

| 日期 | 假设 | 改动 | 指标（端到端 / subgoal） | 失败原因或结论 |
|---|---|---|---|---|
| 2026-11-09 | 子目标 checklist + 门控恢复可提升轮式双臂家庭长程 Q-score/E2E | 新增 `openpi.rsi` + CPU 训练脚本；数据按 subgoal 覆盖过滤 | baseline E2E 0.025 / Q 0.156 → checklist E2E 0.200 / Q 0.325（Δ+0.175 / +0.169） | 值得继续；π0 真训因无 GPU 阻塞 |

## 经验区（一次性记录；长期规则回写 `.cursor/rules/rsi-core.mdc`）

- 无 GPU 时仍可用固定家庭套件 stub 验证评测口径与数据过滤杠杆，但必须标注「非 B1K 官方分」。
- 门控恢复只在子目标失败时触发一次重试，避免干扰已成功步骤（对齐 OopsieRecover 精神）。
