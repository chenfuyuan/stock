## MODIFIED Requirements

### Requirement: 提供长期知识库入口层
系统 SHALL 在 Obsidian 库中提供可由脚本初始化的长期知识库入口，使用户能够从每日分析入口进入公司、主题、事件、行业/催化、证据和复盘相关页面。

#### Scenario: 初始化长期知识库入口
- **WHEN** 使用日期 `2026-05-10` 初始化包含股票 `炼石航空`、代码 `000697.XSHE` 的分析目录
- **THEN** 系统 MUST 生成或保留可链接到公司、主题、事件、行业/催化、证据和复盘入口的 Obsidian Markdown 页面

#### Scenario: 每日入口连接长期知识库入口
- **WHEN** 生成 `vault/stock/2026-05-10/index.md`
- **THEN** 文件 MUST 包含指向长期知识库入口页面的 wikilink

### Requirement: 支持主题和事件沉淀入口
系统 SHALL 提供主题、事件与行业/催化沉淀入口，使跨日期、跨公司的研究材料可以通过 Obsidian wikilink 被持续关联。

#### Scenario: 生成主题、事件和行业/催化入口
- **WHEN** 初始化任意日期的分析目录
- **THEN** 系统 MUST 生成或保留主题入口、事件入口和行业/催化入口 Markdown 页面，并包含可供后续追加研究材料的章节骨架

#### Scenario: 主题、事件和行业/催化入口使用 Obsidian 元数据
- **WHEN** 读取主题入口、事件入口和行业/催化入口 Markdown 页面
- **THEN** 文件 MUST 包含 YAML frontmatter、tags 和一级标题

### Requirement: 保持既有核心入口可用
系统 SHALL 保持 `vault/companies/` 与 `vault/stock/<date>/` 作为公司长期档案和每日分析的核心入口，不得要求用户迁移到全新根目录才能继续使用既有工作流。

#### Scenario: 初始化后保留公司和日期入口
- **WHEN** 初始化包含至少一只股票的分析目录
- **THEN** 系统 MUST 创建或保留 `vault/companies/` 与 `vault/stock/<date>/` 下的既有公司档案、日评和每日综合文档
