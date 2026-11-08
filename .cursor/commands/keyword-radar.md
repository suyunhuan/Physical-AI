执行关键词与方向雷达（RSI pipeline C2），刷新关键词库与业务方向。

按以下 5 路来源串行检索近 7 天信号（每路带回 5-10 条，宁缺毋滥）。检索对象是“具身长程家庭任务的开放技术路线”，不是只找 VLA：
A. 社区热度：Hugging Face Trending、GitHub Trending、arXiv cs.RO/cs.AI/cs.CV/cs.LG 高讨论榜、Papers with Code、X/Twitter、Reddit r/Robotics
B. 国内外大厂 / 机器人公司：Physical Intelligence、Google DeepMind、Figure、Tesla Optimus、Meta FAIR、NVIDIA、Boston Dynamics 等公开进展
C. 创业公司：1X、Skild、Physical Intelligence 同类初创、国内外具身创业公司的公开动态
D. 明星学校与实验室：Stanford、UC Berkeley BAIR、MIT、CMU、ETH、苏黎世联邦理工、清华、北大、上海 AI Lab、智源等新论文
E. 公众号与中文社区：机器之心、量子位、新智元、PaperWeekly 等解读
每路都要检查非 VLA 路线：TAMP/符号规划、世界模型/MPC、RL/自改进、仿真与 sim2real、3D 场景图/记忆/affordance、安全恢复与评测。

步骤：
1. 先读 rsi/keywords.md 确认基线。
2. 每条信号输出：方向 / 关键词、一句话说明、来源（链接 / 平台 / 账号 / 标题）、
   热度信号（榜单排名 / 讨论量级）、与家庭长程任务的相关性（高 / 中 / 低 + 一句理由）。
3. 去重合并后输出"方向雷达日报"：
   - Top 5 新方向（每条含技术路线分类、一句话、来源与热度信号、与家庭长程任务的相关性、建议动作：纳入关键词 / 仅关注 / 暂不跟进）
   - 路线覆盖矩阵：8 类种子及新增路线各自检索状态、命中数量、代表论文、最近覆盖时间；指出当天被忽略的路线和补检建议。不评估代码仓兼容性。
   - 关键词增删建议（新增附理由；降权保留历史，不直接删除）
   - 业务方向刷新建议
4. 按建议更新 rsi/keywords.md（标注日期、来源热度与技术路线），雷达日报写入 rsi/daily/YYYY-MM-DD-radar.md。

约束：每条信号必须附真实来源，不得编造，检索不到标"未覆盖"；相关性必须落到具身家庭长程任务，禁止泛泛 AI 热点。非 VLA 路线必须纳入扫描；没有合格信号时如实说明，不能把 π/openpi 当作唯一技术范式。
