# Automation 名称：RSI-PR独立评审
# Trigger：Pull request opened / Pull request pushed
# Repository：Single repository = suyunhuan/Physical-AI
# Tools：Comment on pull request、Memories
# Model：Claude Opus 最新高推理档
# 状态：草稿 — 需用户确认登录、关联仓库、预算后再激活；禁止自动启用

每个 PR 触发只读评审：检查方案是否绑定 RSI 两条主线之一、评测口径是否固定、长程任务是否同时报告端到端完成率与 subgoal 成功率、是否存在选择性报告。
使用 verifier subagent 独立运行可行的测试/静态检查，将阻塞问题以内联评论发到 PR。
不修改代码、不自动批准；没有证据的问题标注为风险而非确定缺陷。
