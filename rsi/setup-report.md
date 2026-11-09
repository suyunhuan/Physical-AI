# RSI 安装报告 · Physical-AI
# 日期：2026-11-09（更新：套餐已解锁；控制台创建仍缺浏览器登录会话）
# 仓库：https://github.com/suyunhuan/Physical-AI

## 0. 合并与部署进度

| 项 | 结果 |
|---|---|
| PR #1 openpi+RSI 树 | **已合并** `main`（`2a0b81c`） |
| 用户套餐 / Cloud Agents | **用户确认已解锁** |
| 控制台 5 Automations | **尚未创建**（Agent 浏览器停在 `authenticator.cursor.sh`，无会话） |
| 权重 / 训练 / 真机 | **未执行** |

## 1. 已落盘（`main`）

Rules / 8 Commands / 3 Subagents / 5 Automation **仓库草稿** / `rsi/*` 模板 / `rsi/model-selection.md` — 均已在 `main`。

## 2. Automations 控制台状态（逐条）

| # | 名称 | URL | created? | enabled? | 状态 |
|---|---|---|---|---|---|
| 1 | RSI-关键词雷达 | — | no | no | **blocked**：需 cursor.com 登录会话 |
| 2 | RSI-每日论文日报 | — | no | no | **blocked**：同上 |
| 3 | RSI-单点Idea闭环 | — | no | no | **blocked**：同上 |
| 4 | RSI-PR独立评审 | — | no | no | **blocked**：同上 |
| 5 | RSI-自迭代调度 | — | no | no | **blocked**：同上 |

**工具尝试（2026-11-09）**：computer-use 打开 automations → 重定向登录页；无 Automations 创建 API（仅 UUID 查询）。套餐解锁 ≠ 本 VM 浏览器已登录。

**续配路径 A（推荐）**：打开 [Try Live](bc-088004b6-f8ec-5860-a27e-d489b3dea0f0#desktop) → 在该桌面登录 Cursor → 回复「已登录」→ Agent 代建 5 条。  
**续配路径 B**：本机打开 https://cursor.com/automations/new ，按下面 §4 **一次性粘贴**。

手册默认：先保存 **Disabled** → 手动 Run 通过后再 Enable。当前因未创建，**无可 Enable 项**；创建后建议先 Disabled，Run 通过再启用 1/2/4/5（3 保持 Manual）。

## 3. 已测试 / 未测试

### 已测试
- [x] PR #1 合并
- [x] 套餐解锁（用户声明）
- [x] 浏览器访问 automations → 登录墙（无会话）

### 未测试
- [ ] 控制台创建 / 手动 Run / Enable
- [ ] 本地 `/`、Rules、业务命令
- [ ] 权重 / 训练 / 真机

## 4. 一次性填写清单（路径 B · 逐字段）

入口：https://cursor.com/automations/new  
Repository 一律：`suyunhuan/Physical-AI`（Single repository）  
初始：**Disabled**（Save）→ 手动 Run → 再 Enable。

---

### 4.1 RSI-关键词雷达
| 字段 | 值 |
|---|---|
| Name | `RSI-关键词雷达` |
| Trigger | Scheduled · cron `30 6 * * *` |
| Repository | `suyunhuan/Physical-AI` |
| Tools | Memories；可选 MCP；**关** PR 评论 / Slack |
| Model | Gemini 最新 Pro 长上下文档 |
| Enabled | **先 Off** |

**Prompt（整段粘贴）：**
```
读取 .cursor/rules/rsi-core.mdc、rsi/keywords.md 与 rsi/paper-log.md。
按社区热度、机器人公司/大厂、创业公司、高校实验室、中文社区 5 路检索近 7 天信号，并按 8 类开放技术路线归类。
输出 rsi/daily/YYYY-MM-DD-radar.md，并更新 rsi/keywords.md：新增关键词必须附日期、来源、相关性和技术路线；降权必须保留历史理由。
必须检查路线覆盖矩阵；若 VLA 以外路线没有信号，明确标注“未覆盖”并补检，不得用 VLA 结果凑满 Top 5。
将“本次关键词变更摘要”写入 Automation Memory；只提交 rsi/daily 与 rsi/keywords.md 的变更，不修改代码。
若检索源不可用，标注“未覆盖”，不得编造来源。
```

---

### 4.2 RSI-每日论文日报
| 字段 | 值 |
|---|---|
| Name | `RSI-每日论文日报` |
| Trigger | Scheduled · cron `0 7 * * *` |
| Repository | `suyunhuan/Physical-AI` |
| Tools | Memories；**关** Slack / PR Comment |
| Model | Gemini 最新 Pro 长上下文档 |
| Enabled | **先 Off** |

**Prompt：**
```
先读取 rsi/paper-log.md 和 rsi/keywords.md；paper-log 是去重唯一硬依据，Memory 仅用于加速识别。
检索近 7 天 arXiv cs.RO/cs.AI/cs.CV/cs.LG 与公开论文源，做开放技术路线扫描，选择 3 篇前沿 Top + 1-2 篇短期强相关论文。
候选必须标注技术路线，优先补检最近 7 次运行覆盖不足的路线；如果当天候选全是 VLA，补检 TAMP、世界模型/MPC、RL/自改进、仿真数据、感知记忆或安全评测方向。只收录合格工作，不为满足路线配额降低证据或相关性标准。
逐篇输出 idea 卡片（字段遵循 rsi-core，必须含技术路线；不得在研读阶段因无法直接映射 openpi 而排除论文），写入 rsi/daily/YYYY-MM-DD.md。
把本次推送追加到 rsi/paper-log.md，并在同一分支提交 rsi/daily 与 rsi/paper-log.md。
若当天没有合格强相关论文，允许只推 3 篇前沿 Top，并在日报中说明原因；不得为凑数编造论文。
```

---

### 4.3 RSI-单点Idea闭环
| 字段 | 值 |
|---|---|
| Name | `RSI-单点Idea闭环` |
| Trigger | Manual 或 Webhook |
| Repository | `suyunhuan/Physical-AI` |
| Tools | Memories；可选 MCP；**允许创建 PR** |
| Model | Claude Opus 最新高推理档 |
| Enabled | **先 Off**（Manual 可随时 Run） |

**Prompt：**
```
对输入 idea 执行最小验证闭环：读结构基线 → 最小可回退改动 → 小规模训练/仿真 → 固定口径评测 → 报告。
先调用 planner subagent 输出计划；实现后调用 verifier subagent 独立验收。
报告写入 rsi/reports/YYYY-MM-DD-<idea-slug>.md，实验四元组写入 rsi/experiments/experiment-tree.md。
所有改动进入独立分支并开 PR；verifier 未通过时禁止标记 ready for review。
```

---

### 4.4 RSI-PR独立评审
| 字段 | 值 |
|---|---|
| Name | `RSI-PR独立评审` |
| Trigger | Pull request opened / Pull request pushed |
| Repository | `suyunhuan/Physical-AI` |
| Tools | Comment on pull request；Memories |
| Model | Claude Opus 最新高推理档 |
| Enabled | **先 Off** → Run/验证后建议 Enable |

**Prompt：**
```
每个 PR 触发只读评审：检查方案是否绑定 RSI 两条主线之一、评测口径是否固定、长程任务是否同时报告端到端完成率与 subgoal 成功率、是否存在选择性报告。
使用 verifier subagent 独立运行可行的测试/静态检查，将阻塞问题以内联评论发到 PR。
不修改代码、不自动批准；没有证据的问题标注为风险而非确定缺陷。
```

---

### 4.5 RSI-自迭代调度
| 字段 | 值 |
|---|---|
| Name | `RSI-自迭代调度` |
| Trigger | Scheduled · cron `0 18 * * 5` |
| Repository | `suyunhuan/Physical-AI` |
| Tools | Memories；可选 MCP；允许创建 PR |
| Model | Claude Opus 最新高推理档；轻量步骤可用 Auto/Composer |
| Enabled | **先 Off** → 验证后建议 Enable |

**Prompt：**
```
读取 rsi/experiments/experiment-tree.md、rsi/reports 与 rsi/plans，生成本周 RSI 复盘：
有效改动、失败假设、指标变化、下一轮预算建议。只允许提出最多 3 个下一步候选，按预期收益/成本/风险排序。
若候选可自动验证，创建独立分支执行最小实验；否则只输出 rsi/experiments/YYYY-MM-DD-rsi-report.md 并等待人工批准。
预算用尽即停；禁止无预算限制地持续改代码。
```

---

### 创建后建议 Enable 顺序
1. 每条先 **手动 Run 一次**（确认只动 `rsi/`、去重读 paper-log）。  
2. 通过后 Enable：**关键词雷达、每日论文日报、PR 独立评审、自迭代调度**。  
3. **单点 Idea 闭环** 可保持 Manual（需要时再 Run）；勿在未设预算时对它开自动大规模训练。

## 5. 阻塞项

| 阻塞 | 需要 |
|---|---|
| Agent VM 浏览器无 cursor.com 会话 | [Try Live](bc-088004b6-f8ec-5860-a27e-d489b3dea0f0#desktop) 登录，或用户本机按 §4 粘贴 |
| 无 Automations 写 API | 只能 UI 创建 |
| 创建后的手动 Run / Enable | 用户或登录后的 Agent |

## 6. 验收对照

| 项 | 状态 |
|---|---|
| RSI 文件在 `main` | 已完成 |
| 5 Automation 控制台对象 | **未创建** |
| Enabled | **无** |
| 选模文档 | `rsi/model-selection.md` 已有 |
