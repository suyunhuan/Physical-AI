# RSI 模型选择映射（安装日：2026-11-08）

> 原则：手册按**系列与能力档位**推荐；此处映射到本环境当前可见的模型 ID。界面下拉名称可能与 slug 略有差异，请以 Cursor 模型选择器实际选项为准。
>
> **本文件只做映射建议，不声称已在 Cursor UI / Automations 控制台完成选模。**

## 1. 当前环境可见模型系列（本 Agent 可用 slug）

| 系列 | 可用 slug 示例 | 对应手册档位 |
|---|---|---|
| Gemini | `gemini-4-argon-{low,medium,high}` | Gemini Pro 长上下文档 → 优先 `gemini-4-argon-high` |
| GPT Sol | `gpt-5.6-sol-{none,low,medium,high,xhigh,max}`（及 `-fast`） | GPT Sol 档 → 优先 `gpt-5.6-sol-high` 或更高 |
| Claude Opus | `claude-opus-5-5-{low,medium,high,xhigh,max}` | Claude Opus 高推理档 → 优先 `claude-opus-5-5-high` / `xhigh` |
| Claude Sonnet | `claude-sonnet-5-5-{low,medium,high,xhigh,max}` | Sonnet 档总结任务 |
| Composer / Auto | `composer-2.5`、`composer-2.5-fast`；UI 中的 Auto | 轻量监控、归档、检索子任务 |
| 其他 | `claude-fable-5-1-thinking-*`、`cursor-grok-4.6-*`、`grok-4.7-*`、`muse-wonder-1.0-*` | 非 RSI 默认主路径，按需选用 |

## 2. 本地 Cursor Agent / Subagents 映射

| RSI 环节 | 手册推荐 | 本环境映射 | 人工操作 |
|---|---|---|---|
| C1 `paper-daily` | Gemini Pro 最新长上下文档 | 父 Agent：`gemini-4-argon-high`；检索子任务：Auto / `composer-2.5-fast` | 本地会话模型下拉选 Gemini 高档；Max Mode **保持关闭** |
| C2 `keyword-radar` | Gemini Pro；简单日更可用 Auto | 汇总：`gemini-4-argon-high`；5 路检索：Auto / Composer | 同上 |
| C3 `idea-loop` | Claude Opus 高推理档 | 父 Agent：`claude-opus-5-5-high`（或 `xhigh`） | Agent 模式 + Opus；设迭代预算 |
| C4 `feature-design` | GPT Sol 或 Claude Opus | 父：`gpt-5.6-sol-high` 或 `claude-opus-5-5-high` | 方案阶段优先 Sol |
| C5 `parallel-dev` | Claude Opus | `claude-opus-5-5-high` | worktree 隔离 |
| C6 `exp-run` | Auto/Composer；异常切 Opus | 监控：Auto / `composer-2.5`；诊断：`claude-opus-5-5-high` | 异常再升级 |
| C7 `retro` | Auto / Sonnet | Auto 或 `claude-sonnet-5-5-medium` | — |
| C8 `rsi` | Opus 或 Premium 强模路由 | `claude-opus-5-5-high` / `xhigh`；归档用 Auto | 必须设停止预算 |

### Subagent frontmatter（已写入 `.cursor/agents/`）

| Subagent | 手册写法 | 落盘 `model` 字段 | 说明 |
|---|---|---|---|
| `planner` | GPT Sol 档 | `gpt-5.6-sol` | 若 UI 解析失败，改为账号下拉中最新 Sol 档 ID |
| `implementer` | `inherit` | `inherit` | 跟随父 Agent |
| `verifier` | `claude-opus-5[effort=high]` | `claude-opus-5[effort=high]` | 若当前解析器要求完整 slug，改为 `claude-opus-5-5-high` 或带 effort 的等价写法 |

## 3. Automations（Cloud Agent）映射

| Automation | Trigger | 手册 Model | 本环境建议选模 | 状态 |
|---|---|---|---|---|
| RSI-关键词雷达 | `30 6 * * *` | Gemini Pro 长上下文 | UI 选 Gemini 最新 Pro / `gemini-4-argon-high` 等价项 | **待界面操作**（未激活） |
| RSI-每日论文日报 | `0 7 * * *` | Gemini Pro 长上下文 | 同上 | **待界面操作** |
| RSI-单点Idea闭环 | Manual / Webhook | Claude Opus 高推理 | UI 选 Opus 最新高档 | **待界面操作** |
| RSI-PR独立评审 | PR opened/pushed | Claude Opus 高推理 | 同上 | **待界面操作** |
| RSI-自迭代调度 | `0 18 * * 5` | Opus；轻量步骤 Auto | Opus + 轻步骤 Auto/Composer | **待界面操作** |

Cloud Automations **没有**本地 Max Mode 开关；控费靠：选模档位、Repository 限定为 `suyunhuan/Physical-AI`、Prompt 只读 `rsi/` 与必要代码、设置运行预算。首次全部保持**禁用**，手动 Run 验证后再考虑启用定时。

## 4. Max Mode

- **本地**：默认关闭。仅在单次需要装下超大上下文（大量 openpi 文件 / 长实验日志 / 完整论文集）时临时开启，结束后关闭。
- **Automations**：无 Max Mode 开关；按模型最大支持上下文运行 —— 不要在 Prompt 里写“关闭 Max Mode”。

## 5. 无法由本安装 Agent 完成的界面步骤

1. Cursor Settings → Models：确认上述模型对本账号可见且有额度。
2. Settings → Rules：确认 project rules（`.cursor/rules/rsi-core.mdc`）被加载 / Always Apply。
3. 本地 Chat 模型选择器：按上表切换；确认 Max Mode off。
4. `cursor.com/automations`：按 `.cursor/automations/*.md` 创建 5 条草稿，选 Repository=`suyunhuan/Physical-AI`、对应 Model 与 Tools；**先禁用**，用户确认预算与权限后再手动 Run / 启用。
