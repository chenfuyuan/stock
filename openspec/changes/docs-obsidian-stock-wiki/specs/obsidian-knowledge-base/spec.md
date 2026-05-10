## ADDED Requirements

### Requirement: 提供股票研究 Wiki 顶层导航
系统 SHALL 在 Obsidian 知识库中提供股票研究 Wiki 顶层导航，使用户能够从统一入口访问公司长期认知、行业、专题、来源证据、市场摘要、每日分析、研究问题和维护页面。

#### Scenario: 生成股票研究 Wiki 入口
- **WHEN** 初始化或更新股票研究知识库入口
- **THEN** `vault/index.md` MUST 包含指向 `vault/companies/`、`vault/industries/`、`vault/themes/`、`vault/raw/`、`vault/market/`、`vault/stock/`、`vault/questions/`、`vault/maintenance/` 的 Obsidian wikilink 或路径入口

### Requirement: 维护知识库操作日志
系统 SHALL 在 Obsidian 知识库中维护按时间追加的操作日志，用于记录 ingest、query、lint、analysis 等知识库维护动作。

#### Scenario: 记录一次分析动作
- **WHEN** 为 `炼石航空(000697.XSHE)` 生成 `2026-05-10` 的每日分析
- **THEN** `vault/log.md` MUST 追加包含日期、动作类型、股票标识、主要输出路径和数据依据摘要的记录

### Requirement: 区分 raw 证据快照与大体量明细
系统 SHALL 将 `vault/raw/` 限定为 LLM 可安全阅读的证据快照层，并排除全市场逐股票行情、全市场资金流、分钟线和逐笔等大体量明细数据。

#### Scenario: 接收文档型来源
- **WHEN** 新增公司公告、新闻、政策文件、研报摘要或 PDF 来源
- **THEN** 系统 MUST 允许将其归档到 `vault/raw/` 的相应来源目录并记录来源日期或检索时间

#### Scenario: 接收每日市场汇总
- **WHEN** 新增指数、总成交额、涨跌家数、涨跌停统计或行业/概念汇总等小体量复盘数据
- **THEN** 系统 MUST 允许将其保存到 `vault/raw/data/market-summary/<date>/` 并生成包含来源、采集时间和字段口径的 metadata

#### Scenario: 接收全市场行情明细
- **WHEN** 待保存数据为全 A 逐股票行情、全市场资金流、分钟线或逐笔明细
- **THEN** 系统 MUST 不将该数据写入 `vault/raw/` 或 `vault/stock/<date>/`

### Requirement: 分离每日研究输出与长期公司认知
系统 SHALL 保持 `vault/stock/<date>/` 作为每日研究输出位置，并保持 `vault/companies/` 作为跨日期长期公司认知位置。

#### Scenario: 生成某日个股分析
- **WHEN** 为 `炼石航空(000697.XSHE)` 生成 `2026-05-10` 的每日分析
- **THEN** 系统 MUST 将该次分析输出到 `vault/stock/2026-05-10/`，并只把跨日期仍成立的长期认知更新到 `vault/companies/`

### Requirement: 记录研究报告的数据依据
系统 SHALL 要求每日研究报告记录数据源、获取时间、查询区间以及数据文件路径或 Obsidian 来源页面。

#### Scenario: 报告引用窗口型接口数据
- **WHEN** 每日研究报告使用 Tushare 或 akshare 拉取的近一年行情或资金流数据
- **THEN** 报告 MUST 记录数据源、获取时间、查询区间和 `data/runs/<date>/<symbol>/` 下的本次数据文件路径
