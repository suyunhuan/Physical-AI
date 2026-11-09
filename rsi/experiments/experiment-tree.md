# experiment-tree.md · 实验树与经验沉淀
# 维护人：suyunhuan　最近更新：2026-11-09（新增 subgoal-progress-eval）

## 实验四元组（假设 / 改动 / 指标 / 失败原因）

| 日期 | 假设 | 改动 | 指标（端到端 / subgoal） | 失败原因或结论 |
|---|---|---|---|---|
| 2026-11-09 · `subgoal-progress-eval`（R8 主 / R2 次，主线 1） | LIBERO 的 BDDL goal 合取式可以逐项读取为固定口径的 subgoal 原子，从而在不改动 rollout 与成功判定的前提下，同时产出端到端完成率与 subgoal 级进度 / regression 指标 | 新增 `openpi_client.eval`（通用 tracker + 聚合器 + LIBERO BDDL 适配层，Python 3.8 兼容）；`examples/libero/main.py` 以 `--report-subgoal-metrics`（默认 **off**）接入每步原子采样与 JSONL/summary 落盘；新增 `scripts/subgoal_metrics_replay.py` 确定性回放 | **端到端 / subgoal 真实数值：未采集（阻塞）**。本次只采到评测器自身指标：单元测试 27 passed、桩环境集成测试 6 passed、确定性回放 17 个数值聚合字段 + first_achieved_step 全部匹配手算（exit 0）、既有测试回归 71 passed、ruff 通过、回放脚本在 CPython 3.8.20 下完整跑通 | **部分完成，值得继续。** 评测器核心已验证且可完整回退。阻塞：无 GPU / 无 pi0 权重 / LIBERO·robosuite·MuJoCo 未安装 → 真实 rollout 未跑；CPU `debug` 训练烟雾测试**基线即 OOM**（exit 137，anon-rss 13.99GB），根因 `src/openpi/models/pi0.py:84` 把 SigLIP 硬编码为 `So400m/14`，`paligemma_variant="dummy"` 不缩小视觉塔，与本次改动无关。不能声称满足硬规则 8，也不能声称任何策略性能变化。报告：`rsi/reports/2026-11-09-subgoal-progress-eval.md` |

## 经验区（一次性记录；长期规则回写 `.cursor/rules/rsi-core.mdc`）

- **LIBERO 的 `done` 就是 BDDL goal 的合取**：`third_party/libero` 在 pin 住的 `f78abd6` 上，`bddl_base_domain.py:807` 写 `done = self._check_success()`；注意基类 `bddl_base_domain.py:779-786` 的 `_check_success` 只是 `return False` 的桩，真正的 AND 实现在 6 个 problem 子类里（如 `libero_tabletop_manipulation.py:135-143`），对 `parsed_problem["goal_state"]` 的每个 predicate 调 `_eval_predicate` 后做 AND。因此逐项读取同一批 predicate 得到的进度轨迹与环境成功位按构造一致，`done=True` 时必须全部 atom 为真，可当一致性自检（`done_atom_mismatch`）。
- **LIBERO 评测容器是 Python 3.8，且不含 openpi 主包**：`examples/libero/Dockerfile` 用 `uv venv --python 3.8`，`PYTHONPATH` 只有 `/app`、`packages/openpi-client/src`、`third_party/libero`。凡是要同时被 pytest 收集又被评测容器导入的代码，只能放 `packages/openpi-client`，并保持 3.8 兼容（用 `from __future__ import annotations` 配合 `X | None`，既满足 ruff py311 口径又能在 3.8 跑）。
- **`examples/` 默认不被 pytest 收集**（`pyproject.toml` `testpaths = ["src","scripts","packages"]`），但显式传路径可以覆盖 testpaths。所以 `examples/libero/main_test.py` 这类桩环境集成测试要在文档里写明显式命令，否则等于没人跑。
- **本机（15GB / 4 vCPU / 无 GPU）跑不了 openpi 的 CPU 训练烟雾测试**：`paligemma_variant="dummy"` 只缩小 LLM，`pi0.py:84` 的 SigLIP `So400m/14` 图像塔不受影响，约 400M 参数的 float32 参数+梯度+Adam 动量直接 OOM。下次想做训练回归，要么申请 GPU/大内存机器，要么先给图像塔加一个 dummy 变体（属于独立 idea，不要混进别的实验）。
- **评测器故障必须与策略故障分开记账**：插桩失败的 episode 要保留在端到端分母里并单列 `instrumentation_coverage`，否则一个坏掉的 adapter 会悄悄缩小被报告的样本集，这正是硬规则 6「禁止选择性报告」要防的情况。同理，被基础设施故障（策略服务器挂掉、推理超时）中断的 episode 必须带 `termination_reason` 标记 —— 否则它会以一条低 progress 的「正常 episode」身份拉低 subgoal 指标。这两点都是 verifier 独立复核时才发现的。
- **verifier subagent 可能跑不了 Shell**（本次 `readonly: true` 使其只能做静态取证）。遇到这种情况要如实记录「运行时证据由主 agent 执行」，不要把静态复核包装成完整验收；但静态复核仍然很有价值 —— 本次它找出了 py3.8 不兼容、文件归属错误、回放字段覆盖不全、异常会计口径 4 个真问题。
- **自动化触发可能不带 idea 载荷**：本次「RSI-单点Idea闭环」手动触发的 body 为空（digest 为空串的 sha256），且 `rsi/daily`、`rsi/plans` 尚无 idea 池。这种情况下按 rsi-core 的主线自选 idea 并在报告里写明来源，不要空跑。
