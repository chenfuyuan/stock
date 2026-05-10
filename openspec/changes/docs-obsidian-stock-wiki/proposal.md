## Why

当前 A 股研究工作流已经会产出公司档案与每日分析，但 Obsidian 知识库还缺少统一的数据分层、目录边界和 LLM 维护约束，导致来源材料、行情数据、长期认知和每日输出容易混杂。

现在需要把 `docs/llm-wiki.md` 的轻量 Markdown Wiki 思路落到股票研究场景中，使知识库可持续维护，同时避免 Claude Code 读取行情和资金流大文件造成上下文膨胀。

## What Changes

- 修改 Obsidian 知识库能力，明确 `vault/` 中 raw、market、companies、stock、index、log 等知识层职责。
- 修改结构化股票数据底稿能力，明确 Tushare/akshare 窗口型数据按本次分析 run 重新生成并覆盖。
- 新增每日市场汇总快照边界，允许小体量复盘数据进入 `vault/raw/data/market-summary/`。
- 新增大体量行情/资金流明细排除边界，禁止默认采集全 A 明细或放入 Obsidian raw。
- 强化研究报告的数据依据记录，要求标注数据源、获取时间、查询区间和数据文件路径。

## Capabilities

### New Capabilities

### Modified Capabilities
- `obsidian-knowledge-base`: 明确股票研究 Obsidian 知识层目录职责、raw 证据边界、市场摘要页、索引日志与跨页面链接要求。
- `structured-stock-data-draft`: 调整 Tushare/akshare 结构化数据存放与刷新策略，区分市场汇总快照、目标股票池数据、窗口型接口数据和大体量明细数据。

## Impact

- 影响 OpenSpec 能力：`obsidian-knowledge-base`、`structured-stock-data-draft`。
- 影响文档与工作流约定：`vault/` 知识库目录、`data/runs/` 分析数据目录、LLM 维护索引与日志的流程。
- 不引入新的运行时依赖、数据库 schema、定时任务、向量检索或自动交易能力。
