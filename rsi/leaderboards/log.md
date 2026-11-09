# log.md · 榜单雷达运行日志（每次运行追加一行）
# 维护人：suyunhuan　由「具身榜单雷达」自动追加
# 主榜 B1K（Q-score，100 任务 BDDL partial credit）；卫星榜 RoboCasa365（Overall，50 任务平均成功率 %）

| 运行日期 | 快照文件 | B1K verified #1（Q / SR） | B1K Top-5 门槛 Q | RoboCasa365 #1（Overall） | 相对上次变化 | 一句话摘要 |
|---|---|---|---|---|---|---|
| 2026-11-09 | [2026-11-09-board.md](2026-11-09-board.md) | The North Star / HiPhys-RSI　0.6828 / 48.2% | 0.4951（Autolab A²WLA） | HexaShell 1.5（Agent，HexaFuture）85.6 | 首次运行，无上次；以 B1K 2025 存档榜（#1 test Q 0.2599）为参照，榜首 Q ×2.63 | 首次快照：B1K 2026 六条 verified 结果落地，榜首为华为「The North Star」的 HiPhys-RSI（冻结 VLM coding agent 构建并自改进可执行 pipeline，推理期按任务路由到 pipeline 或 VLA），Q 0.6828 领先第 2 名 +10.9%；第 2、3 名（IF1001 / Cyber）均为 WAM 但细节未公开；#4/#5（Anyverse A²MEAS / Autolab A²WLA）有 arXiv:2611.09124 与开源承诺，是 Top-5 中可复现性最好的一支。RoboCasa365（11-01 更新）同样由 Agent 类 HexaShell 1.5 登顶（85.6，vs 最强 VLA 62.6），WAM 占第 2 梯队——两榜一致显示榜首已不是单体 VLA。纯 π0.5 微调退为基线带（第三方严格复现 Q≈0.39，官方 RoboCasa365 π0.5 基线 16.9）。关键失败模式：搜索密集/遮挡任务耗尽时间预算、组合泛化断崖（π0.5 在 Composite-Unseen 仅 1.2%）、自报→核验落差（A²MEAS −0.144 Q）、评测噪声地板 ΔQ≈±0.06、以及 gripper 释放阈值与 stage belief 未恢复等接口级陷阱。verified 分数对应 public 还是 hidden instance 未核实；Outstanding Open Source 奖项归属、IF1001/Cyber/XYRobot 方法细节均未覆盖。 |
