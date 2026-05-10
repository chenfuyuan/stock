## Why

当前 Obsidian 输出已经能按公司与日期生成报告，但长期使用时仍容易形成按天堆叠的报告文件，缺少跨日期、跨公司、跨主题和跨事件的稳定沉淀入口。现在需要在不推翻既有 A 股日评工作流的前提下，把 `vault/` 升级为可导航、可复盘、可由脚本持续生成的投研知识库底座。

## What Changes

- 修改每日报告脚手架，使生成结果能稳定连接公司、日评、每日综合文档和长期知识库入口。
- 新增 Obsidian 知识库组织能力，定义主题、事件、证据、复盘等长期沉淀层的可生成入口。
- 新增研究沉淀能力，使研究结论、证据来源和后续验证点可以被日后回看和验证。
- 保留现有公司页和日评目录作为核心入口，不移除既有 `vault/companies/` 与 `vault/stock/YYYY-MM-DD/` 工作流。

## Capabilities

### New Capabilities
- `obsidian-knowledge-base`: 定义可长期增长的 Obsidian 投研知识库入口、长期沉淀层和跨页面链接要求。
- `research-follow-up`: 定义研究结论、证据、验证点与复盘记录的可沉淀要求。

### Modified Capabilities
- `obsidian-report-scaffolding`: 扩展现有 Obsidian 报告脚手架的生成要求，使每日输出连接到长期知识库底座。

## Impact

- 影响 `vault/` 下公司页、日评、每日入口页和每日综合文档的目录与链接规范。
- 影响 `templates/` 中 Obsidian Markdown 模板的 frontmatter、tags、wikilinks 和章节骨架。
- 影响 `scripts/init_daily_reports.py` 及相关测试对生成文件、幂等行为和链接内容的断言。
- 不引入新的外部数据源、抓取系统、自动主题发现能力或交易建议能力。
