# RSI 安装报告 · Physical-AI
# 日期：2026-11-08（更新：PR #1 已合并；Automations 控制台仍阻塞）
# 仓库：https://github.com/suyunhuan/Physical-AI
# 当前文档分支：`cursor/automations-status-bf70`（跟进状态更新）

## 0. 同步与合并状态

| 项 | 结果 |
|---|---|
| 安装前 Physical-AI 状态 | 仅 Initial commit + `# Physical-AI` README |
| openpi 引入方式 | unrelated-histories merge（非 force-push） |
| Submodules | `third_party/aloha`、`third_party/libero` 已 init |
| **PR #1** | **已合并** → `main`（merge commit `2a0b81c`，2026-11-08T16:24:47Z） |
| 权重 / GPU 训练 / 机器人部署 | **未执行** |

## 1. 已落盘

### 1.1 代码基座
- openpi 历史已在 `main`
- 结构核对：`src/openpi/models`、`src/openpi/training`、`scripts/train.py`、`third_party/libero`

### 1.2 Cursor RSI 配置树
| 类别 | 路径 | 数量 | 状态 |
|---|---|---|---|
| Rules | `.cursor/rules/rsi-core.mdc` | 1 | 已落盘（`main`） |
| Commands | `.cursor/commands/*.md` | 8 | 已落盘 |
| Subagents | `.cursor/agents/*.md` | 3 | 已落盘 |
| Automation Prompts | `.cursor/automations/*-automation.md` | 5 | **仓库草稿已落盘；控制台对象未创建** |
| 状态模板 | `rsi/keywords.md`、`rsi/paper-log.md`、`rsi/experiments/experiment-tree.md` | 3 | 已落盘 |
| 子目录 | `rsi/daily/`、`reports/`、`plans/`、`experiments/` | 4 | 已落盘 |
| 选模映射 | `rsi/model-selection.md` | 1 | 已落盘 |

## 2. 待界面操作

1. Cursor Settings → Rules：确认 Always Apply 加载 `rsi-core.mdc`。
2. 本地选模按 `rsi/model-selection.md`；**Max Mode 默认关闭**。
3. `/` 菜单确认 8 个 commands；Subagent frontmatter 解析按需改 ID。
4. **Automations**：用户已授权登录/关联仓库/预算/激活，但仍需在浏览器完成 cursor.com 登录（见 §4）。
5. Cloud Agents 套餐：若 Upgrade 墙出现需先升级。
6. GPU / 权重 / 真机：仍未配置（本任务不涉及）。

## 3. 已测试 / 未测试

### 已测试
- [x] PR #1 合并进 `main`（`gh pr merge`，无冲突）
- [x] openpi 合并 + submodule + RSI 静态树
- [x] 浏览器打开 `cursor.com/automations`（被重定向至 `authenticator.cursor.sh`，无会话）
- [x] 确认无 Automations 创建 API（仅 `get-automation` 按 UUID 查询）

### 未测试
- [ ] 本地 `/` 命令、Rules 加载、Subagent 拉起
- [ ] `/paper-daily` / `/keyword-radar` 业务运行
- [ ] Automations 控制台创建 / 手动 Run / Scheduled 启用
- [ ] 权重下载、训练、真机

## 4. Automations 状态（2026-11-08 跟进）

**用户授权**：已明确授权登录、关联仓库、预算与激活。  
**工具结论**：Cloud Agent 无 `/automate`、无可写 Automations API；computer-use 浏览器无 cursor.com 登录会话 → **5 条均未在控制台创建，亦未启用**。

| # | 名称 | Trigger | 控制台状态 | 原因 |
|---|---|---|---|---|
| 1 | RSI-关键词雷达 | Scheduled `30 6 * * *` | **blocked** | 需 cursor.com 登录后创建 |
| 2 | RSI-每日论文日报 | Scheduled `0 7 * * *` | **blocked** | 同上 |
| 3 | RSI-单点Idea闭环 | Manual / Webhook | **blocked** | 同上 |
| 4 | RSI-PR独立评审 | PR opened / pushed | **blocked** | 同上 |
| 5 | RSI-自迭代调度 | Scheduled `0 18 * * 5` | **blocked** | 同上 |

### 剩余用户点击清单（精确）

入口：[cursor.com/automations/new](https://cursor.com/automations/new)（或本机 Cursor `/automate`）

对每条 Automation：

1. **登录** cursor.com（Google / GitHub / Apple / Email 任一）。
2. 确认套餐含 **Cloud Agents**；若提示 Upgrade → 先升级。
3. **New Automation** → Name / Trigger / Repository=`suyunhuan/Physical-AI` / Tools / Model 按下表填写。
4. Prompt：粘贴对应 `.cursor/automations/*.md` 中标题注释以下的指令正文。
5. 保存后 **先手动 Run 一次**，确认只改 `rsi/`、去重读 `paper-log`。
6. 通过后按授权 **Enable**（建议优先启用 1、2、4、5；3 保持 Manual 可跑即可）。

| 名称 | Trigger | Tools | Model | Prompt 文件 |
|---|---|---|---|---|
| RSI-关键词雷达 | cron `30 6 * * *` | Memories；可选 MCP | Gemini 最新 Pro 长上下文 | `.cursor/automations/keyword-radar-automation.md` |
| RSI-每日论文日报 | cron `0 7 * * *` | Memories | Gemini 最新 Pro 长上下文 | `.cursor/automations/paper-daily-automation.md` |
| RSI-单点Idea闭环 | Manual / Webhook | Memories；可选 MCP；允许 PR | Claude Opus 高推理档 | `.cursor/automations/idea-loop-automation.md` |
| RSI-PR独立评审 | PR opened / pushed | Comment on PR；Memories | Claude Opus 高推理档 | `.cursor/automations/pr-review-automation.md` |
| RSI-自迭代调度 | cron `0 18 * * 5` | Memories；可选 MCP；允许 PR | Opus；轻量 Auto | `.cursor/automations/rsi-automation.md` |

可选：在 Agent 桌面 [Try Live](bc-088004b6-f8ec-5860-a27e-d489b3dea0f0#desktop) 登录后，可继续让 Agent 代填控制台。

## 5. 阻塞项

| 阻塞 | 影响 | 需要 |
|---|---|---|
| cursor.com 浏览器未登录 | 无法创建/启用 5 条 Automation | 用户登录（Live 桌面或本机控制台） |
| 无 Automations 写 API | Agent 无法纯 API 创建 | 控制台或登录后的浏览器 |
| Cloud Agents 套餐未在控制台验证 | 可能 Upgrade 墙 | 用户确认套餐 |
| GPU / 权重 / 真机 | 阻塞训练与部署实验 | 另授权（本任务不做） |

## 6. 验收对照（手册 §8）

| 项 | 状态 |
|---|---|
| RSI 文件落盘 | **已在 `main`** |
| Always Apply / `/` 菜单 / Subagent | **待本机确认** |
| 5 Automation 控制台对象 | **未创建（blocked）** |
| `model-selection.md` | 已落盘 |
| Max Mode 本地 off | 文档已写；UI 待确认 |
| Automations 启用 | **未启用**（创建被登录阻塞） |

## 7. 后续

1. 用户登录 cursor.com 后按 §4 创建并启用（或开 Live 桌面让 Agent 续填）。
2. 本机完成 Rules / 选模 / Max Mode。
3. 业务运行仍建议先本地 `/keyword-radar` → `/paper-daily`；不下载权重、不开训。
