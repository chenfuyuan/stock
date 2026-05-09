# Pre-Design: feature-evidence-pack

## 1. Problem & Goals
- 真实问题：当前股票数据抓取可能生成过大的 JSON，尤其是全量历史行情数据；如果把这些原始 payload 直接传给 Claude Code，会撑爆上下文，但不一定提升分析准确性。
- 目标：在保留准确、可追溯本地事实源的同时，减少默认传递给 Claude Code 的内容。
- 目标：先保存原始 JSON，再从原始 JSON 派生面向具体分析任务的小型 Evidence Pack。
- 目标：高频行情数据默认控制在有用窗口内，同时保留完整财务历史以支持长期周期分析。
- 非目标：不构建完整因子平台，不引入数据库化投研系统，不重写现有报告模板。

## 2. Constraints / Invariants
- 原始 JSON 是本地事实源，必须可用于重新生成 Evidence Pack。
- Claude Code 默认必须读取 Evidence Pack，而不是读取完整原始 JSON。
- 行情、资金流等高频数据默认保留最近一年。
- 财务数据允许在原始 JSON 中全量保留，因为长期周期、拐点和历史对比依赖完整财务序列。
- 当前事实必须保留数据日期、抓取时间、来源和状态元数据。

## 3. Direction & Key decisions
- 推荐路线：先保存原始 JSON，再从原始 JSON 生成面向任务的 Evidence Pack 供 Claude Code 使用。
- 放弃路线：抓取时只写固定摘要 JSON —— 理由：这会把当前分析视角固化到数据层，后续复算或深入检查会更困难。
- 放弃路线：每次都让 Claude Code 读取原始 JSON 并临时编写解析代码 —— 理由：准确性可以保留，但无法稳定控制上下文大小。
- 关键决策：采用 raw-first 持久化；理由是 Evidence Pack 必须可复算、可审计。
- 关键决策：Evidence Pack 作为默认分析输入；理由是上下文控制不能依赖每次人工提醒。
- 关键决策：行情窗口默认一年；理由是足够覆盖趋势、波动、量价和资金流背景，同时避免全量历史膨胀。
- 关键决策：财务原始数据保留全量；理由是长期对比是股票分析核心，且财务行数通常可控。
- 关键决策：维护小型 JSON fixture 或 shape 示例；理由是通用解析和一次性解析脚本都需要字段结构，但不需要携带完整历史数据。

## 4. Guardrails for downstream
- 必须遵守：原始 JSON 可以本地落盘，但不能作为 Claude Code 默认 prompt 或输入材料。
- 必须遵守：Evidence Pack 必须包含可追溯元数据，例如 `raw_path`、生成时间、数据日期或抓取时间、来源和状态信息。
- 必须遵守：Evidence Pack 必须从原始 JSON 生成，并且不需要重新联网抓取即可复算。
- 必须遵守：行情和资金流 payload 默认使用一年窗口，除非后续需求明确扩大窗口。
- 必须遵守：财务数据进入 Evidence Pack 时必须按任务选择或聚合，不能整块复制全量财务原始数据。
- 禁止脑补：不要新增数据库层、因子引擎或完整投研平台。
- 禁止脑补：不要把重写现有报告模板纳入本次 change。
- 禁止脑补：不要默认把完整原始 JSON 传入 Claude Code prompt。
- 禁止脑补：不要用模型训练数据替代当前抓取数据。
- 禁止脑补：不要在生成产物中保存 token、`.env` 或本地私密配置。

## Next step
- 建议下一步：`/opsx:ff`
- 复杂度信号：边界已经清晰，主要工作是调整抓取范围、定义 raw/evidence 文件约定、增加 Evidence Pack 生成与 fixture，并用测试覆盖。
