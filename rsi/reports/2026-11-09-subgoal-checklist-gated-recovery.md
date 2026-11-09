# 验证报告：子目标 Checklist + 门控恢复

**日期**：2026-11-09  
**Idea**：在 openpi RSI 层落地 B1K 对齐的子目标 checklist，并在轮式双臂家庭固定套件上用门控恢复提升 Q-score / E2E。  
**评测口径**：`FIXED_EVAL_SUITE`（8 任务）× 5 episodes = 40 episodes；指标 = mean Q-score + E2E success rate。

## 背景
对齐日报强相关：`OopsieRecover` 门控纠偏、`RoboCasa-Mem` 阶段完成率；服务榜单冲顶的 Q-score 口径。本环境 **无 GPU**，π0 权重微调阻塞；完成 CPU 最小训练 + 闭环仿真。

## 改动摘要
- `src/openpi/rsi/subgoal_checklist.py` — Q-score / E2E
- `src/openpi/rsi/wheeled_bimanual_sim.py` — 固定家庭套件闭环
- `src/openpi/rsi/checklist_policy.py` — 策略头 + 数据过滤 + CPU 训练
- `scripts/rsi/run_first_idea_loop.py` — 一键跑通

## 训练
| 项 | 值 |
|---|---|
| 设备 | CPU |
| 步数 | 400 |
| 过滤后样本 | 800（positive_rate≈0.616） |
| 终态 acc | ≈0.618 |
| 阻塞 | 无 nvidia-smi → 无法 π0 fine-tune / 拉权重 |

## 评测对比（固定套件）

| 方法 | mean Q-score | E2E success |
|---|---|---|
| baseline open-loop | **0.156** | **0.025** |
| checklist + gated recovery | **0.325** | **0.200** |
| Δ | **+0.169** | **+0.175** |

可视化：`rsi/experiments/first-idea-artifacts/{train_curves,suite_metrics,per_task_qscore}.png`

## 结论
**值得继续**：子目标账本 + 门控重试在固定家庭套件上同时抬升部分学分与端到端成功率。  
下一步：GPU 到位后把同一口径接到 π0 动作块重排序 / 真实 B1K 或 RoboCasa 轨迹。

## 风险
- 当前 sim 为可复现 stub，**不是**官方 B1K 分数  
- 无真机、无权重；不得把本结果申报为榜单成绩

## 本机 GPU / 真 openpi 续跑
见 `rsi/docs/local-gpu-openpi-b1k.md`：
- Mac：`--mode cpu-stub|all-safe`
- Linux+CUDA：`DOWNLOAD_WEIGHTS=1 python3 scripts/rsi/run_openpi_train.py --config pi0_libero_checklist_smoke`
