# Design: docs-obsidian-stock-wiki

## Context
- 本设计承接 `pre_design.md`、`proposal.md` 与两个 delta specs，目标是把 `docs/llm-wiki.md` 的轻量 Markdown Wiki 模式落到 A 股研究 Obsidian 知识库。
- 当前项目已有 `vault/companies/` 与 `vault/stock/YYYY-MM-DD/` 的股票研究输出约束，但缺少 raw、market、data、index、log 等目录的清晰职责边界。
- 核心设计约束是知识层与数据层分离：Obsidian 中只放 LLM 可安全阅读的证据、摘要、索引、数据指针和研究结论，避免 Claude Code 读取行情/资金流大文件造成上下文膨胀。
- 项目尚未正式使用，因此可以直接替换旧的结构化数据输出约定，不需要兼容双写或迁移历史报告。

## Goals / Non-Goals
- Goals：定义股票研究 Obsidian Wiki 的目录职责、数据分层、LLM 维护流程和研究报告数据依据契约。
- Goals：将结构化接口数据从 `vault/stock/<date>/data/<code>.json` 调整为 `data/runs/<date>/<symbol>/` 下的本次分析 run 数据。
- Goals：明确 `vault/raw/` 可接收的证据快照范围，以及大体量行情/资金流明细的排除边界。
- Non-Goals：不做自动交易，不生成买卖点、止盈止损、仓位或交易执行建议。
- Non-Goals：不做定时全自动抓取、全 A 每日明细采集、复杂 RAG、向量库或 embedding 检索系统。
- Non-Goals：不实现具体数据采集脚本、数据库 schema、SQL 查询接口或自动化任务调度。

## Decisions

### 1. 采用 `vault/` 知识层 + `data/runs/` 分析数据层
- `vault/` 是 Obsidian 与 LLM 的知识层，只保存可浏览、可引用、上下文安全的 Markdown、证据快照、摘要、索引和研究结论。
- `data/runs/YYYY-MM-DD/<symbol>/` 是每次分析生成的接口数据层，用于保存近一年日线、近一年资金流、近 N 日同行对比等窗口型数据。
- `vault/stock/YYYY-MM-DD/` 只保存每日研究报告、每日汇总和索引页，不再保存接口明细数据。
- 替代方案“全部放入 `vault/`”被放弃，因为它依赖人工纪律避免读取大文件，容易让 raw 边界再次模糊。

建议目录边界：

```text
vault/
  index.md
  log.md
  raw/
  companies/
  industries/
  themes/
  market/
  stock/YYYY-MM-DD/
  questions/
  maintenance/

data/
  runs/YYYY-MM-DD/<symbol>/
```

### 2. 采用五类数据生命周期规则
- 文档型证据长期进入 `vault/raw/`：公告、新闻、政策、PDF、研报摘要、公司 IR 资料等。
- 低频小体量结构化证据可进入 `vault/raw/data/`：财务三表、股东数据、分红、质押等适合 LLM 直接阅读的公司证据快照。
- 每日市场汇总按日期进入 `vault/raw/data/market-summary/YYYY-MM-DD/`：指数、总成交额、涨跌家数、涨跌停统计、行业/概念汇总等复盘资料。
- Tushare/akshare 窗口型接口数据进入 `data/runs/YYYY-MM-DD/<symbol>/`，同一 run 内整窗重新生成并覆盖，不做增量同步。
- 大体量明细默认不采集且不进入 `vault/raw/`：全 A 逐股票行情、全市场资金流、分钟线、逐笔、板块成分每日明细等。

### 3. 采用 `ingest / analysis / query / lint` 四操作流程
- `ingest` 处理新来源材料，写入 `vault/raw/` 或来源摘要，并更新相关公司、行业、专题页面与 `vault/log.md`。
- `analysis` 生成每日股票分析，写入 `vault/stock/YYYY-MM-DD/`，必要时保守更新 `vault/companies/`、`vault/market/entities/`、`vault/index.md` 与 `vault/log.md`。
- `query` 回答研究问题，若答案有长期沉淀价值，则写入 `vault/questions/`、专题页或相关公司/行业页，并补齐 backlinks。
- `lint` 周期性检查孤儿页、缺少来源、过期结论、raw/data 边界违规、缺失索引和缺失日志记录。
- 所有操作都应先读 `vault/index.md` 与 `vault/log.md` 定位相关页面，只更新相关范围，不做全库大扫除。

### 4. 采用报告 `数据依据` 小节 + run metadata 的双记录契约
- 每份每日研究报告必须包含 `数据依据` 小节，记录数据源、获取/检索时间、查询区间、run 数据路径和 Obsidian 来源页面。
- 每个 `data/runs/YYYY-MM-DD/<symbol>/` 必须包含 metadata，记录股票标识、分析日期、数据窗口、接口来源、生成/覆盖时间、文件清单、字段口径、缺失字段和失败接口。
- 报告不复制全量行情或资金流明细，只引用路径、来源页面和必要统计摘要。
- 若未来清理 run 数据，报告仍必须保留关键统计摘要、数据源、获取时间和查询区间，保证最低限度可追溯。

### 5. 正式使用前直接切换新结构，移除旧输出约定
- 新分析只写 `data/runs/YYYY-MM-DD/<symbol>/`，不再写 `vault/stock/YYYY-MM-DD/data/<code>.json`。
- 由于项目尚未正式使用，不做历史数据迁移、不双写旧路径、不保留兼容 shim。
- 实施阶段必须检查并替换所有指向 `vault/stock/<date>/data/<code>.json` 的脚本、模板、spec 依赖和文档引用。
- `structured-stock-data-draft` 的新行为以本 change 的 MODIFIED requirements 为准。

### 6. 用五类风险护栏约束后续实现
- 上下文膨胀：禁止大体量明细进入 `vault/raw/`；Claude 查询结构化数据时只读本次 run 的小窗口或小结果集；不得扫描长期全量行情或资金流。
- 路径碎片化：`vault/` 固定一层核心分类，窗口型接口数据统一归入 `data/runs/YYYY-MM-DD/<symbol>/`。
- 数据可追溯：报告 `数据依据`、run metadata、`vault/log.md` 三者共同记录分析动作和数据输入。
- 接口口径变化：metadata 记录来源、获取时间、查询区间、字段口径和缺失字段；同一 run 内覆盖刷新，不跨 run 增量合并。
- LLM 过度维护：公司长期页只写跨日期仍成立的认知，单日波动保留在 `vault/stock/YYYY-MM-DD/` 或 `vault/market/daily/`。

## Risks / Trade-offs
- `data/runs/` 增加一层路径复杂度 → 用报告 `数据依据` 小节和 run metadata 固定引用契约。
- run 数据可能被清理，导致旧报告无法复核明细 → 报告保留关键统计摘要、数据源、获取时间和查询区间。
- `vault/raw/` 边界可能再次模糊 → 明确 raw 只接收 LLM 可安全阅读的证据快照和小体量市场汇总。
- Tushare/akshare 接口口径可能变化 → metadata 记录字段口径、缺失字段和获取时间，同一 run 内覆盖保证本次输入一致。
- LLM 可能过度更新长期公司页 → 只把跨日期仍成立的结论写入 `vault/companies/`，单日现象留在日评或市场页。
- 不引入完整自动校验工具会降低强制性 → 本次先在模板、任务自检和 lint 操作说明中落实护栏，后续可单独增强自动校验。

## Migration Plan
- 正式使用前直接替换旧路径约定：新结构化接口数据只写 `data/runs/YYYY-MM-DD/<symbol>/`。
- `vault/stock/YYYY-MM-DD/` 只保留研究报告、每日汇总和索引页，不再保留 `data/<code>.json` 明细目录。
- 删除或更新所有生成、读取、引用 `vault/stock/<date>/data/<code>.json` 的脚本、模板和文档说明。
- 不迁移历史数据、不双写旧路径、不保留兼容 shim；如发现临时旧产物，重新生成到新 run 目录。
- 回滚方式是恢复旧输出路径模板，但只有在正式使用前验证发现新结构无法满足报告生成时才考虑。