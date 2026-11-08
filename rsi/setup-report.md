# RSI 安装报告 · Physical-AI
# 日期：2026-11-08
# 仓库：https://github.com/suyunhuan/Physical-AI
# 分支：`cursor/sync-openpi-rsi-bf70`

## 0. 同步动作摘要

| 项 | 结果 |
|---|---|
| 安装前 Physical-AI 状态 | 仅 Initial commit + `# Physical-AI` README（远端 size≈0） |
| openpi 引入方式 | `git remote add openpi` → `fetch openpi/main` → `merge --allow-unrelated-histories`（保留双方历史，非 force-push） |
| README 冲突 | 保留 openpi 全文，顶部增加 Physical-AI / RSI 说明 |
| Submodules | 已 `git submodule update --init --recursive`（`third_party/aloha`、`third_party/libero`） |
| 权重 / GPU 训练 / 机器人部署 | **未执行**（按约束） |

## 1. 已落盘

### 1.1 代码基座
- openpi `main` 历史已合并进本仓库工作分支
- 已核对典型结构存在：`src/openpi/models`、`src/openpi/training`、`scripts/train.py`、`third_party/libero`

### 1.2 Cursor RSI 配置树
| 类别 | 路径 | 数量 |
|---|---|---|
| Rules | `.cursor/rules/rsi-core.mdc` | 1 |
| Commands | `.cursor/commands/{paper-daily,keyword-radar,idea-loop,feature-design,parallel-dev,exp-run,retro,rsi}.md` | 8 |
| Subagents | `.cursor/agents/{planner,implementer,verifier}.md` | 3 |
| Automation Prompts（草稿） | `.cursor/automations/*-automation.md` | 5 |
| 状态模板 | `rsi/keywords.md`、`rsi/paper-log.md`、`rsi/experiments/experiment-tree.md` | 3 |
| 子目录 | `rsi/daily/`、`rsi/reports/`、`rsi/plans/`、`rsi/experiments/` | 4 |
| 选模映射 | `rsi/model-selection.md` | 1 |

静态检查：上述文件与目录均存在；无覆盖既有实验日志（安装前 `rsi/` 不存在）。

## 2. 待界面操作（未声称已配置）

1. **Cursor Settings → Rules**：确认 project rules 发现 `.cursor/rules/rsi-core.mdc` 且 Always Apply 生效。
2. **本地模型选择器**：按 `rsi/model-selection.md` 为 C1–C8 选模；**Max Mode 默认关闭**。
3. **命令菜单**：在本地 Chat/Composer 输入 `/`，确认 8 个自定义命令可见。
4. **Subagent 解析**：确认 `planner` / `implementer` / `verifier` frontmatter 可被当前 Cursor 解析；若 `claude-opus-5[effort=high]` 或 `gpt-5.6-sol` 解析失败，按 `rsi/model-selection.md` 改为账号下拉中的等价最新 ID。
5. **Automations 控制台**（见 §4 清单）：登录、关联 `suyunhuan/Physical-AI`、选模、设预算、**先禁用保存**；**未经用户确认不得激活**。
6. **套餐 / Cloud Agents 权限**：若控制台提示 Upgrade，需先升级到含 Cloud Agents 的计划。
7. **GPU / 训练预算 / 机器人硬件**：本安装未验证；进入 C3/C6 前需用户确认资源。

## 3. 已测试 / 未测试

### 已测试
- [x] 远端仓库可读写（fetch / 即将 push）
- [x] openpi 历史非破坏合并 + submodule checkout
- [x] RSI 目录树静态存在性检查（1 rule / 8 commands / 3 agents / 5 automation prompts / rsi 模板与子目录）
- [x] Automation Prompt 头字段含 Trigger / Repository / Tools / Model / 禁用状态说明
- [x] 本 Cloud Agent 环境可见模型系列已写入 `rsi/model-selection.md`

### 未测试
- [ ] 本地 `/` 命令菜单实际触发
- [ ] project rules 在新会话中实际加载
- [ ] Subagent 实际拉起与 frontmatter 模型解析
- [ ] `/paper-daily`、`/keyword-radar` 端到端运行（安装阶段按手册跳过）
- [ ] worktree / 并行 subagent 隔离
- [ ] Automations 控制台创建、手动 Run、Scheduled 启用
- [ ] `/automate` 本地斜杠命令（见下）
- [ ] 任何模型权重下载、微调、LIBERO 评测、真机部署

## 4. `/automate` 可用性与控制台填写清单

**结论：本 Cloud Agent 会话无法代为调用本地 `/automate`，也无可写的 Automations 创建 API（仅有按 UUID 查询的 `get-automation`）。请用户在本机 Cursor 或 [cursor.com/automations/new](https://cursor.com/automations/new) 按下列清单填写；Prompt 正文直接粘贴仓库内对应文件。**

| # | 名称 | Trigger | Repository | Tools | Model（建议） | Prompt 文件 | 初始状态 |
|---|---|---|---|---|---|---|---|
| 1 | RSI-关键词雷达 | Scheduled `30 6 * * *` | `suyunhuan/Physical-AI` | Memories；可选 MCP | Gemini 最新 Pro 长上下文 | `.cursor/automations/keyword-radar-automation.md` | **禁用** |
| 2 | RSI-每日论文日报 | Scheduled `0 7 * * *` | 同上 | Memories | Gemini 最新 Pro 长上下文 | `.cursor/automations/paper-daily-automation.md` | **禁用** |
| 3 | RSI-单点Idea闭环 | Manual / Webhook | 同上 | Memories；可选 MCP；允许 PR | Claude Opus 高推理档 | `.cursor/automations/idea-loop-automation.md` | **禁用** |
| 4 | RSI-PR独立评审 | PR opened / PR pushed | 同上 | Comment on PR；Memories | Claude Opus 高推理档 | `.cursor/automations/pr-review-automation.md` | **禁用** |
| 5 | RSI-自迭代调度 | Scheduled `0 18 * * 5` | 同上 | Memories；可选 MCP；允许 PR | Opus；轻量步骤 Auto | `.cursor/automations/rsi-automation.md` | **禁用** |

用户确认项（激活前必须）：① Cursor 登录与 Cloud Agents 套餐；② 仓库 `Physical-AI` 已关联；③ 用量/预算上限；④ 每条先手动 Run 一次通过。**当前未激活任何 Automation。**

## 5. 阻塞项（不猜测）

| 阻塞 | 影响 | 需要 |
|---|---|---|
| Automations 需用户在控制台创建并确认预算 | 云端定时雷达/日报无法自动跑 | 用户登录 + 关联仓库 + 预算确认 |
| Cloud Agents 套餐是否可用 | 未在本机验证 | 用户在控制台确认；若需 Upgrade 则先升级 |
| 本地 UI 选模 / Max Mode / Rules 加载 | Agent 无法改用户本机设置 | 按 §2 人工操作 |
| GPU（≥微调 22.5GB / 全量 70GB）未验证 | 阻塞 C3/C6 训练 | 用户提供机器或延后实验 |
| 模型权重未下载（约束禁止） | 无法推理/微调 | 用户明确授权后再拉 checkpoint |
| 真机 / 机器人访问 | 阻塞真实机长程评测 | 用户提供平台与安全规程 |

## 6. 验收对照（手册 §8，安装视角）

| 项 | 状态 |
|---|---|
| `rsi-core.mdc` 落盘 | 已落盘；Always Apply **待界面确认** |
| 8 commands | 已落盘；`/` 菜单 **未测试** |
| 3 subagents | 已落盘；解析 **未测试** |
| 5 automation prompts | 已落盘；控制台 **待界面操作** |
| `keywords` / `paper-log` / 5 子目录 | 已落盘（experiments 含 experiment-tree；其余 `.gitkeep`） |
| 本地 `/paper-daily` / `/keyword-radar` | **未测试**（安装阶段跳过） |
| Automation 手动 Run | **未测试** |
| `rsi/model-selection.md` | 已落盘 |
| Max Mode 本地 off；云端无开关 | 文档已写明；UI **待确认** |
| worktree 隔离验证 | **未测试** |
| Automations 保持禁用 | Prompt 已标注禁用；控制台创建后仍须用户保持禁用直至确认 |

## 7. 后续建议（非本安装范围）

1. 合并本 PR 后，在本地 Cursor 打开 `Physical-AI`，完成 §2 界面项。
2. 用户确认后，按 §4 创建 5 条 Automation（仍禁用）→ 各手动 Run 一次 → 再考虑启用 3 条定时。
3. 首次业务运行建议：`/keyword-radar` → `/paper-daily`（仍不下载权重、不开训）。
