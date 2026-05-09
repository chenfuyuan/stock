# Design: feature-stock-analysis-workflow

## Context

- 本 change 承接 `pre_design.md`：第一版目标是建立可重复、可审计、适合 Obsidian 的 A 股深度投研工作流。
- 上游 `proposal.md` 将能力拆为 `stock-pool-parsing`、`obsidian-report-scaffolding`、`structured-stock-data-draft`、`stock-analysis-workflow` 四类。
- 上游 specs 已限定可测试行为：股票池解析、目录与模板初始化、Tushare/akshare 数据底稿、skill 执行顺序和质量门槛。
- 关键约束详见 `pre_design.md` §2：当前事实需带来源/日期、报告不得给具体交易建议、token 不得泄露、v1 不引入 Web 服务/MCP/多 agent 编排。

## Goals / Non-Goals

- Goals：实现轻量三层工作流：确定性 Python 脚本、Obsidian Markdown 模板、`stock-analysis` skill 编排。
- Goals：让用户粘贴 A 股股票池后，Claude Code 能稳定完成解析、初始化、结构化数据底稿、联网检索、来源分级、报告写作和质量自检。
- Non-Goals：不实现全自动投研系统，不做 MCP，不做自定义多 agent，不引入数据库、任务队列或服务化运行时。
- Non-Goals：不让 Tushare/akshare 取代公告、新闻、政策、行业叙事等联网检索。

## Decisions

1. 顶层架构采用三层划分：`scripts/` 负责确定性动作，`templates/` 负责 Obsidian 文件骨架，`.claude/skills/stock-analysis/SKILL.md` 负责 Claude 编排与质量门槛。
   - 理由：解析、目录初始化和数据底稿抓取可测试且可复跑；联网检索、来源分级和投研判断仍由 Claude 在 skill 约束下完成。
   - 替代方案：脚本优先会扩大 v1 自动化范围；文档优先会削弱可测试性和格式稳定性。

2. 脚本间数据契约采用 JSON 管道。
   - `python -m scripts.parse_stock_list` 从 stdin 读取用户粘贴文本，向 stdout 输出 `[{"name": ..., "code": ...}]`。
   - `python -m scripts.init_daily_reports` 与 `python -m scripts.fetch_stock_data` 从 stdin 读取同一 JSON 结构，并向 stdout 输出执行摘要 JSON。
   - 理由：JSON 管道便于 shell 串联、测试断言和用户手动调试，同时避免引入临时文件生命周期管理。

3. Markdown 模板采用轻量 `{{key}}` 字符串替换，不引入 Jinja。
   - 模板文件放在 `templates/`；渲染器只替换调用方提供的变量，未知占位符保留给人工填写。
   - 理由：v1 模板主要是静态骨架，轻量替换足够表达 `date`、`stock_code`、`stock_name`、`stock_pool_links` 等变量。
   - 替代方案：Jinja 表达力更强但增加依赖和模板复杂度；纯 Python 拼接不利于用户直接编辑模板。

4. Tushare 与 akshare 采用双源组合策略。
   - 有 `TUSHARE_TOKEN` 时先运行 Tushare fetcher，同时总是运行 akshare fetcher作为补充和交叉参考。
   - 无 token 时记录 `tushare_status: skipped:no_token` 并继续尝试 akshare。
   - 理由：Tushare 是优先结构化数据源，akshare 能补充资金流等字段；双源并存提升底稿完整性，但两者都不能替代联网检索。

5. 数据抓取失败采用字段级隔离和显式缺失记录。
   - 单个 endpoint 失败只影响对应字段，并写入 fetcher 内部 `missing_fields`。
   - 整个数据源不可用时，编排层写入 `tushare:unavailable` 或 `akshare:unavailable` 等来源级缺失标记。
   - 异常状态中只记录异常类型，不写异常原文，避免库错误信息回显 token。
   - 理由：报告生成不应因一个字段失败而中断，但底稿必须保留可审计的缺失信息。

6. 公司长期档案采用“初始化脚本创建 + Claude 保守更新”的边界。
   - `init_daily_reports` 只在档案缺失时创建模板，且绝不覆盖已有文件。
   - `stock-analysis` skill 允许 Claude 写入 A/B 级、长期稳定信息；短期催化、未确认事项和边界信息写入日评的“建议写入公司档案的信息”。
   - 理由：长期档案是知识库沉淀层，必须避免结构化底稿或短期新闻直接污染长期事实。

架构与数据流：

```text
User stock pool text
  │
  ▼
scripts.parse_stock_list ── JSON list[{name, code}]
  │
  ├─▶ scripts.init_daily_reports ── companies/ + stock/YYYY-MM-DD/*.md
  │
  └─▶ scripts.fetch_stock_data ─── stock/YYYY-MM-DD/data/<code>.json
                                      ▲
                                      ├─ Tushare fetcher（token 可用时）
                                      └─ akshare fetcher（补充/回退）

Claude Code stock-analysis skill
  ├─ 读取模板产物、公司档案、JSON 底稿
  ├─ 联网检索公告/新闻/政策/行业背景
  ├─ 来源分级与事实核验
  └─ 写入日评、综合文档、入口页，并执行质量门槛
```

## Risks / Trade-offs

- [Risk] akshare 或 Tushare 接口字段、列名、限流行为变化导致底稿缺失 → Mitigation：fetcher 单元测试 mock 当前契约，运行时将缺失写入 `missing_fields`，skill 在研究日志中记录数据限制。
- [Risk] 轻量模板替换无法表达复杂条件逻辑 → Mitigation：v1 模板保持静态骨架，复杂判断留给 Claude 写作阶段；只有当模板复杂度真实上升时再评估 Jinja。
- [Risk] skill 约束依赖 Claude 执行纪律，不能像代码一样强制所有投研边界 → Mitigation：把关键边界写入 skill 的 execution sequence 与 quality gates，并在项目 `CLAUDE.md` 保留触发硬规则。
- [Risk] 双源组合增加一次分析的网络调用数量和失败面 → Mitigation：两类 fetcher 相互隔离，任何单源失败都不阻塞报告生成。
- [Risk] 公司长期档案保守更新可能漏掉应沉淀的信息 → Mitigation：日评保留“建议写入公司档案的信息”，让用户后续确认后再沉淀。

## Migration Plan

- 第一步：补齐 Python 项目脚手架、依赖声明、`.env.example`、`.gitignore`、`companies/` 与 `stock/` 根目录。
- 第二步：按 TDD 实现 `scripts/` 能力与模板渲染、目录初始化、双源数据底稿抓取。
- 第三步：新增 `.claude/skills/stock-analysis/SKILL.md`，把执行顺序、来源分级、报告结构和质量门槛固化为 Claude Code workflow。
- 第四步：运行全量测试与小样本 smoke test；smoke-test 生成的样例数据是否保留或提交必须由用户确认。
- 回滚策略：本 change 不涉及数据库或外部部署；如需回滚，移除新增脚本、模板、skill、测试与样例输出即可，不能删除用户已有研究档案。
