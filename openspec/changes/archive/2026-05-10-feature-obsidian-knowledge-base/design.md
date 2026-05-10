# Design: feature-obsidian-knowledge-base

## Context
- 当前 `vault/companies/` 与 `vault/stock/YYYY-MM-DD/` 已经能生成公司页、日评和每日综合文档，但整体仍缺少全库级长期入口。
- 本设计继承 `pre_design.md` 的渐进式路线：不重建 vault，不引入自动主题发现，不扩展为交易系统。
- `proposal.md` 定义了长期知识库组织、研究跟踪沉淀，以及对既有 `obsidian-report-scaffolding` 的扩展。
- `specs/` 要求系统能生成或保留长期知识库入口、主题/事件/证据/复盘入口，并让每日输出连接到这些入口。

## Goals / Non-Goals
- Goals：让 `vault/` 具备可导航、可复盘、可由脚本持续生成的长期知识库底座，范围与 `pre_design.md` §1 对齐。
- Goals：在不破坏既有公司页和日评入口的前提下，新增长期沉淀层入口和稳定链接规则。
- Non-Goals：不做完整投研方法论重构，不新增外部数据源、抓取系统、自动主题发现或 AI 自动摘要能力。
- Non-Goals：不提供具体买卖价位、止盈止损、仓位建议，也不把本项目扩展为交易系统。

## Decisions
- 全库入口采用 `vault/index.md`：该文件作为 Obsidian 知识库根入口，链接公司档案、每日分析入口和长期沉淀层；相比只复用每日入口，它能避免长期知识库入口被某个日期目录隐藏。
- 长期沉淀层放在 `vault/knowledge/`：该目录承载跨日期增长的知识，不迁移 `vault/companies/` 与 `vault/stock/YYYY-MM-DD/`，从而保持既有工作流可用。
- 长期目录拆为四个独立子目录：`themes/`、`events/`、`evidence/`、`reviews/` 分别承载主题研究、事件跟踪、证据沉淀和复盘记录，每个目录提供一个入口页。
- 脚本职责限定为生成稳定入口、目录和模板骨架：`init_daily_reports` 创建或保留 `vault/index.md`、`vault/knowledge/**/index.md` 与每日输出中的入口链接，不为每只股票自动生成主题、事件、证据或复盘子页。
- Obsidian 链接采用“中文固定入口名 + 英文目录 slug”：目录路径使用英文便于脚本维护，wikilink 使用全库唯一中文名便于阅读，例如 `[[知识库入口]]`、`[[主题研究入口]]`、`[[事件跟踪入口]]`、`[[证据库入口]]`、`[[复盘入口]]`。
- wikilink 继续不携带路径前缀：延续既有 `obsidian-report-scaffolding` 约束，模板中不写 `vault/`、`knowledge/`、`stock/<date>/` 等路径前缀；通过唯一中文入口名降低同名冲突。
- 模板改造采用最小增强：每日入口页补全库入口链接，日评补证据、验证点或复盘入口，研究日志承接待跟踪问题，公司页只补长期跟踪链接，不重排既有日评 14 节结构。
- 幂等策略保持“不覆盖已有文件”：继续以只创建缺失文件为核心；已有公司页、日评、每日综合文档和入口页存在时保留原内容，不做自动 patch。
- 目录与链接关系如下：

```text
vault/
  index.md  -> [[公司档案入口]] / [[每日分析入口]] / [[知识库入口]]
  companies/
  stock/YYYY-MM-DD/
    index.md -> [[知识库入口]] / 个股日评 / 每日综合文档
  knowledge/
    index.md      -> [[主题研究入口]] / [[事件跟踪入口]] / [[证据库入口]] / [[复盘入口]]
    themes/index.md
    events/index.md
    evidence/index.md
    reviews/index.md
```

## Risks / Trade-offs
- [Risk] 旧历史报告不会自动获得新链接和新章节 → [Mitigation] 本次只保证新入口和新日期模板可用，历史文件升级后续单独设计安全迁移。
- [Risk] 中文固定 wikilink 可能与用户已有页面同名 → [Mitigation] 入口名必须全库唯一且固定，避免使用过于泛化的名称。
- [Risk] 四个长期目录初期可能为空 → [Mitigation] 只生成入口页和用途骨架，不自动制造大量空子页。
- [Risk] 最小模板增强不会形成完整投研 SOP → [Mitigation] 将研究方法论模板和自动化证据聚合作为后续 change。
- [Risk] 不自动 patch 已有文件会造成新旧模板并存 → [Mitigation] 明确这是保护用户手写研究内容的取舍，迁移需求另行处理。

## Migration Plan
- 新增入口和目录只创建缺失文件：`vault/index.md`、`vault/knowledge/index.md` 与四个长期层入口不存在时创建，存在时跳过。
- 已有 `vault/companies/`、`vault/stock/YYYY-MM-DD/`、公司页、日评和每日综合文档继续保留，不删除、不覆盖、不自动插入区块。
- 新日期初始化使用增强后的模板生成入口链接和沉淀区块；历史报告如需补链，后续单独设计带确认或 marker 的安全迁移能力。
