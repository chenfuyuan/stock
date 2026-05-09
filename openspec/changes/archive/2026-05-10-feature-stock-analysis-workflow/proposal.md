## Why

当前项目需要把每日 A 股股票池分析固定成可重复、可审计、适合 Obsidian 长期沉淀的 Claude Code 工作流，避免每次临场组织目录、模板、数据底稿和来源规则。

`docs/superpowers/` 已经明确第一版目标：用轻量本地脚本、Markdown 模板和 `stock-analysis` skill 建立稳定流程，同时确保当前事实来自联网检索或结构化数据底稿，并严格避免输出具体买卖价位、仓位、止盈止损等投资建议。

## What Changes

- 新增 A 股股票池输入解析、代码规范化和 Tushare 代码转换能力。
- 新增 Obsidian 友好的公司长期档案、个股日评、每日入口页和三份每日综合文档模板。
- 新增每日目录初始化能力，按日期生成 `companies/` 与 `stock/YYYY-MM-DD/` 产物且保持幂等。
- 新增 Tushare 优先、akshare 补充的结构化数据底稿抓取能力，并记录数据日期与缺失字段。
- 新增 `stock-analysis` skill，约束 Claude Code 按固定流程完成联网检索、来源分级、报告写作和质量门槛自检。

## Capabilities

### New Capabilities
- `stock-pool-parsing`: 解析用户粘贴的 A 股股票池并输出规范化股票记录。
- `obsidian-report-scaffolding`: 生成 Obsidian 兼容的公司档案、个股日评和每日综合文档骨架。
- `structured-stock-data-draft`: 获取 Tushare/akshare 结构化数据底稿并以可审计 JSON 保存。
- `stock-analysis-workflow`: 定义 Claude Code 执行 A 股深度投研报告的固定 skill 流程与质量门槛。

### Modified Capabilities

## Impact

- 影响本地 Python 项目结构：新增 `pyproject.toml`、`scripts/`、`tests/`、`templates/`。
- 影响 Claude Code 项目配置：新增 `.claude/skills/stock-analysis/SKILL.md`。
- 影响知识库输出目录：新增或使用 `companies/` 与 `stock/YYYY-MM-DD/`。
- 新增运行依赖：`tushare`、`akshare`、`python-dotenv`；新增开发测试依赖：`pytest`。
- 不引入 MCP、Web 服务、数据库、任务队列或自定义多 agent 编排。
