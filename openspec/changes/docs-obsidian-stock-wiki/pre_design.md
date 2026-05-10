# Pre-Design: docs-obsidian-stock-wiki

## 1. Problem & Goals
- 真实问题：当前项目需要参考 `docs/llm-wiki.md`，为 A 股深度研究搭建一个由 LLM 维护、Obsidian 阅读的股票研究知识库；它需要沉淀公司、行业、专题、来源材料、每日复盘与研究问题，而不是让每次分析都从零检索和组织材料。
- 触发原因：现有项目已经要求输出到 `vault/companies/` 与 `vault/stock/YYYY-MM-DD/`，但还缺少稳定的知识库目录结构、数据分层边界和 LLM 维护流程，尤其需要避免行情/资金流大数据被 Claude Code 直接读取导致上下文膨胀。
- Goals：定义第一版轻量 Markdown Wiki 工作流，使 Obsidian 中的目录结构可浏览、LLM 维护流程可执行，并明确 raw、data、market、companies、stock 等层的职责。
- Goals：明确股票研究数据分层策略，包括文档型证据、小体量低频结构化数据、每日市场汇总、Tushare/akshare 窗口型接口数据、目标股票池数据和大体量明细数据的存放与更新规则。
- Non-goals：本次不做自动交易，不生成买卖点、止盈止损、仓位或交易执行建议。
- Non-goals：本次不做定时全自动抓取、全 A 每日明细采集、复杂 RAG、向量库或 embedding 检索系统。
- Non-goals：本次不实现具体数据采集脚本、数据库 schema、SQL 查询接口或自动化任务调度。

## 2. Constraints / Invariants
- 所有 OpenSpec 产物必须使用中文；必要技术标识、文件路径、命令和代码符号可保留原文。
- 必须遵守项目既有股票研究规则：当前事实必须包含数据日期或检索/获取时间，优先使用公告、交易所、CNINFO、监管/政府、公司 IR、主流财经媒体、可靠数据平台、Tushare、akshare 等来源。
- `vault/companies/` 承载公司长期认知，`vault/stock/YYYY-MM-DD/` 承载每日研究输出；两者职责不能混淆。
- Obsidian 知识层只放 LLM 可安全阅读的证据、摘要、索引、数据指针和研究结论；不得让 Claude Code 自然遍历到大体量行情或资金流明细。
- `vault/raw/` 可以存文档型来源、小体量低频结构化证据和每日市场汇总快照；不等于所有结构化数据都禁止进入 raw。
- 全市场逐股票行情、全市场资金流、分钟线、逐笔等大体量明细数据默认不采集、不放入 `vault/raw/`，如确有需要应放在 Obsidian 外部的数据层或临时 run 目录。
- Tushare/akshare 等接口可再获取的窗口型数据，若采集的是近一年、近 N 日等区间数据，优先在本次分析 run 内整窗重新拉取并覆盖，不做增量同步或扫描本地长期全量。
- 每日明细采集范围由研究需要驱动：只采目标股票池，或对话分析中明确发现需要补充的股票；不要默认采集 A 股全市场每只股票。

## 3. Direction & Key decisions
- 推荐路线：轻量股票研究 Markdown Wiki 工作流 —— 先固化 Obsidian 目录、数据分层和 LLM 维护流程，不引入自动化平台或复杂检索基础设施。
- 放弃路线：自动化数据入库平台 —— 理由：会把本次范围扩大到任务调度、接口稳定性、数据质量校验和失败重试，偏离“先搭建可维护知识库”的目标。
- 放弃路线：RAG/向量检索优先 —— 理由：第一版页面规模和查询需求可先由 `index.md`、`log.md`、文件搜索和清晰目录承载，过早引入检索层会掩盖 wiki 结构尚未稳定的问题。
- 关键决策：采用“知识层与数据层分离” —— `vault/` 是 Obsidian/LLM 可读知识层，`data/` 或 `data/runs/` 是接口数据和临时分析数据层。
- 关键决策：`vault/raw/` 定义为证据快照层 —— 存公告、新闻、研报、政策、PDF、财务三表、股东数据、分红记录、每日市场汇总等小体量或文档型证据。
- 关键决策：每日市场汇总可进入 raw —— 指数、总成交额、涨跌家数、涨跌停统计、行业/概念汇总等小体量复盘资料可保存到 `vault/raw/data/market-summary/YYYY-MM-DD/`。
- 关键决策：大体量明细不进入 raw —— 全 A 逐股票行情、全市场资金流、分钟线、逐笔、板块成分每日明细等不放入 Obsidian 可遍历目录。
- 关键决策：窗口型接口数据按 run 覆盖 —— 如炼石航空近一年日线和资金流，每次分析重新拉取本次窗口并写入 `data/runs/YYYY-MM-DD/000697.XSHE/`，同一 run 内可覆盖刷新。
- 关键决策：研究输出与长期认知分离 —— `vault/stock/YYYY-MM-DD/` 记录某次分析的结论和数据依据，`vault/companies/` 只沉淀跨日期仍成立的长期认知。
- 关键决策：保留索引和日志 —— `vault/index.md` 面向内容导航，`vault/log.md` 面向 ingest/query/lint/analysis 的时间线记录。

## 4. Guardrails for downstream
- Must follow：目录设计必须保持 `vault/companies/` 与 `vault/stock/YYYY-MM-DD/` 作为公司长期认知和每日分析输出的主路径。
- Must follow：每份研究报告必须记录使用的数据源、获取时间、查询区间和数据文件路径或 Obsidian 来源页面。
- Must follow：`vault/raw/` 只能放 LLM 可安全阅读的证据快照，包括文档型来源、小体量低频结构化数据和每日市场汇总。
- Must follow：Tushare/akshare 窗口型数据必须按本次分析窗口重新生成并覆盖本次 run 文件，不要求维护本地长期主表或增量合并。
- Must follow：LLM 维护 wiki 时必须同步考虑索引、日志、相关公司页、行业页、专题页、市场页与当日分析页之间的 wikilinks/backlinks。
- Forbidden to invent：不得把全市场逐股票行情、全市场资金流、分钟线、逐笔等大文件放入 `vault/raw/` 或每日分析目录。
- Forbidden to invent：不得默认每日采集全 A 每只股票数据；采集股票明细必须来自目标股票池或明确的研究问题。
- Forbidden to invent：不得为了增量同步去扫描本地长期全量行情或资金流文件。
- Forbidden to invent：不得把 Tushare/akshare 数据当作公告、新闻、政策、行业背景或市场叙事的替代来源。
- Forbidden to invent：不得生成具体买入价、卖出价、止盈止损、仓位建议，或脑补不存在的公告、新闻、财务数据、行情解释。

## Next step
- 建议下一步：`/opsx:ff`
- 复杂度信号：本次主要是目录结构、数据分层和 LLM 维护流程的规则型 change，不需要先展开复杂架构设计。