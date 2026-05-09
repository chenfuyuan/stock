## ADDED Requirements

### Requirement: 生成每日分析目录结构
系统 SHALL 根据股票记录列表和日期创建 `companies/`、`stock/<date>/`、`stock/<date>/data/`，并为每只股票生成公司长期档案和当日日评文件。

#### Scenario: 首次初始化两只股票
- **WHEN** 输入两只股票并指定日期 `2026-05-10`
- **THEN** 系统 MUST 创建 `companies/<code>-<name>.md`、`stock/2026-05-10/<code>-<name>-日评.md`、`stock/2026-05-10/index.md`、三份每日综合文档和 `stock/2026-05-10/data/`

### Requirement: 初始化过程保持幂等
系统 SHALL 在目标文件已存在时保留原内容，不能覆盖用户已编辑的公司档案、日评或每日综合文档。

#### Scenario: 重复初始化已有公司档案和日评
- **WHEN** 目标公司档案和日评已经存在且包含用户内容
- **THEN** 再次初始化 MUST 保留原文件内容，并在返回摘要中标记对应股票为 skipped

### Requirement: 渲染 Obsidian Markdown 模板
系统 SHALL 使用模板生成带 YAML frontmatter、tags、wikilinks 和固定章节骨架的 Markdown 文件，并替换 `{{date}}`、`{{stock_code}}`、`{{stock_name}}` 等上下文变量。

#### Scenario: 渲染个股日评模板
- **WHEN** 使用股票 `炼石航空`、代码 `000697.XSHE` 和日期 `2026-05-10` 生成日评
- **THEN** 生成文件 MUST 包含对应股票名、代码、日期、公司档案 wikilink，且 MUST 不残留 `{{stock_name}}`、`{{stock_code}}` 或 `{{date}}`

#### Scenario: 渲染每日入口页股票池链接
- **WHEN** 使用两只股票生成 `stock/<date>/index.md`
- **THEN** 入口页 MUST 包含两只股票各自的日评 wikilink 和三份每日综合文档链接

### Requirement: 生成符合报告边界的模板骨架
系统 SHALL 为个股日评提供结论前置的 14 节结构，为公司长期档案提供稳定信息章节，并为每日排序、主题行业综述、研究日志提供独立模板。

#### Scenario: 检查个股日评章节
- **WHEN** 创建个股日评模板文件
- **THEN** 文件 MUST 包含从 `投研结论摘要` 到 `建议写入公司档案的信息` 的 14 个章节，并包含“不构成具体买卖价位、止盈止损或仓位建议”的提示
