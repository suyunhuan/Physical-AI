# 方案：子目标 Checklist + 门控恢复（第一版 idea 闭环）

**日期**：2026-11-09  
**来源**：日报 `OopsieRecover`（门控纠偏）+ `RoboCasa-Mem`（阶段/子目标打分）+ 榜单设计 B1K Q-score  
**H 四元组**

| 轴 | 选择 |
|---|---|
| 任务切片 | 8 条轮式双臂家庭长程链（固定套件 `FIXED_EVAL_SUITE`） |
| 形态 | wheeled base + bimanual（抽象仿真，对齐冲顶形态约束） |
| 数据配方 | 合成示教 + 子目标覆盖过滤（positive rate ≥ 0.4） |
| 评测口径 | 固定套件 × 5 ep/任务；**E2E 成功率** + **Q-score（子目标完成率）** |

## 动机
长程家庭任务单步失败易级联。先落地「子目标账本 + 失败门控重试」的可测闭环，再接到 π0/openpi 真训（需 GPU/权重）。

## 改动面（最小）
- 新增 `src/openpi/rsi/`：checklist 指标、轮式双臂家庭 sim、轻量策略头、数据过滤、CPU 训练
- 入口：`scripts/rsi/run_first_idea_loop.py`
- 不改 π0 主干；不拉 `gs://openpi-assets` 权重

## 训练策略
1. Smoke：单元逻辑 + 短训 40 step  
2. Short train：**CPU 逻辑回归 400 step**（本环境无 GPU，无法跑 π0 LoRA）  
3. 下一步（阻塞解除后）：在 `pi0_libero_low_mem_finetune` 上挂 checklist 过滤后的真实轨迹

## 验收
- 同套件对比 baseline vs checklist+gated  
- 同时报 mean Q-score 与 E2E  
- 产物：metrics.json + 三张图
