# Pre-Design: feature-stock-analysis-workflow

## 1. Problem & Goals
- 真实问题：当前项目需要把每日 A 股股票池分析固定成可重复、可审计、适合 Obsidian 长期沉淀的 Claude Code 工作流，避免每次临场组织目录、模板、数据底稿和来源规则。
- 背景与触发原因：`docs/superpowers/` 已给出 A 股深度投研工作流设计与逐任务实现计划，用户要求实现该目录中的需求。
- Goals：实现第一版工作流，包括本地 Python 辅助脚本、Markdown 模板、`stock-analysis` skill、基础测试与一次端到端烟测路径。
- Goals：支持解析用户粘贴的股票池，创建 `companies/` 与 `stock/YYYY-MM-DD/` 产物，拉取 Tushare/akshare 结构化底稿，并约束 Claude 后续联网检索、来源分级和报告写作。
- Non-goals：不实现全自动投研系统，不做 MCP，不做自定义多 agent 编排，不自动替代人工对公司长期档案的确认判断。
- Non-goals：不把 Tushare/akshare 数据当作最新公告、新闻、政策、行业叙事的替代来源。

## 2. Constraints / Invariants
- 所有 OpenSpec 后续产物必须使用中文编写，保留必要技术标识、路径、命令和代码符号原文。
- 输出必须 Obsidian 友好：YAML frontmatter、tags、wikilinks、backlinks、结论前置。
- 当前事实必须来自本次当前数据或联网检索，并包含数据日期或检索时间；模型训练知识不得作为当前事实依据。
- 来源分级必须保留 A/B/C/未确认边界，C 级或未确认来源不能单独支撑核心结论。
- 报告只能是研究观点，不得输出具体买卖价位、止盈止损或仓位建议。
- token 与本地配置不得写入报告或提交到 git；脚本只能记录 token 是否可用，不能泄露 token 值。
- 第一版必须保持轻量：Python 3.10+、`tushare`、`akshare`、`python-dotenv`、`pytest`，不引入 web framework 或服务化运行时。

## 3. Direction & Key decisions
- 推荐路线：按 `docs/superpowers` 既有设计实现三层轻量工作流——确定性脚本负责机械化动作，模板负责 Obsidian 结构，`stock-analysis` skill 负责编排与质量门槛。
- 放弃路线：构建全自动/多 agent 投研系统 —— 理由：第一版目标是流程稳定和可审计，现阶段多 agent 会增加调度、事实一致性和维护成本。
- 放弃路线：只写 Claude 文档、不实现本地脚本 —— 理由：解析、目录初始化和结构化数据抓取是可确定的机械动作，放在脚本中更可测试、可复跑、可避免格式漂移。
- 关键决策：采用 TDD 推进脚本能力；理由是解析、模板渲染、初始化幂等性和 fetch fallback 都可用单元测试稳定约束。
- 关键决策：Tushare 与 akshare 只生成结构化底稿；理由是它们覆盖行情/财务/资金流等数据，但不能替代公告、新闻、政策和行业叙事检索。
- 关键决策：公司长期档案采用保守更新；理由是长期档案只应沉淀 A/B 级、稳定、长期有效的信息，短期催化和未确认事项留在日评中。
- 关键决策：`stock-analysis` skill 是用户股票池分析的入口；理由是项目硬规则要求用户提供 A 股股票池或请求分析时必须触发该固定流程。

## 4. Guardrails for downstream
- Must follow：实现必须覆盖 `docs/superpowers/plans/2026-05-10-stock-analysis-workflow.md` 中的 v1 范围，不自行扩大到后续扩展项。
- Must follow：脚本、模板和 skill 的接口/路径必须与 `docs/superpowers/specs/2026-05-09-stock-analysis-workflow-design.md` 的输出结构保持一致。
- Must follow：所有脚本涉及 token 的地方必须避免打印、写入 JSON、写入 Markdown 或提交真实值。
- Must follow：初始化流程必须幂等，不能覆盖用户已编辑的公司档案或日评。
- Must follow：测试中所有外部数据源调用必须 mock，不允许单元测试依赖真实网络或真实 token。
- Forbidden to invent：不要新增未在 v1 范围内承诺的 MCP、Web 服务、数据库、任务队列或多 agent 编排。
- Forbidden to invent：不要新增投资建议口径，例如目标价、买卖点、仓位、止盈止损。
- Forbidden to invent：不要把社区传闻、互动平台或二次报道升级为 A/B 级来源。
- Forbidden to invent：不要在没有用户确认时提交 smoke-test 生成的真实样例数据。

## Next step
- 建议下一步：`/opsx:ff-big`
- 复杂度信号：该 change 同时涉及项目脚手架、多个脚本、模板、测试、skill 与端到端验证，且已经存在较完整的需求设计和实施计划，适合走 proposal + specs + design + tasks 的完整路径。
