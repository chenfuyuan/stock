## 1. 项目脚手架

- [x] 1.1 创建 Python 项目配置与依赖声明，包含 `tushare`、`akshare`、`python-dotenv` 和 `pytest`。
- [x] 1.2 创建 `.env.example` 与敏感文件 gitignore 规则，确保 `.env`、`.venv/`、pytest/cache 产物不入库。
- [x] 1.3 创建 `scripts/`、`scripts/fetchers/`、`tests/`、`tests/fetchers/`、`companies/`、`stock/` 的基础目录与包标记。

## 2. 股票池解析

- [x] 2.1 以 TDD 实现 `scripts.parse_stock_list`，支持名称/代码解析、后缀规范化、去重和 stdin→JSON CLI。
- [x] 2.2 以 TDD 实现规范代码到 Tushare 代码的转换，覆盖 `.XSHE/.XSHG/.XBSE` 与 `.SZ/.SH/.BJ`。

## 3. Obsidian 模板与初始化

- [x] 3.1 创建公司长期档案、个股日评、每日入口页、股票池排序、主题行业综述、研究日志模板。
- [x] 3.2 以 TDD 实现轻量模板渲染工具，按 `{{key}}` 替换变量并保留未知占位符。
- [x] 3.3 以 TDD 实现 `scripts.init_daily_reports`，按日期生成完整目录和文件且不覆盖已有内容。
- [x] 3.4 为初始化 CLI 接入 stdin JSON 与 `--date` 参数，并输出 created/skipped 摘要。

## 4. 结构化数据底稿

- [x] 4.1 以 TDD 实现 `scripts.config`，按 `.env` 优先、环境变量兜底读取 `TUSHARE_TOKEN`。
- [x] 4.2 以 mock 测试实现 Tushare fetcher，覆盖基础信息、行情、估值、财务指标与字段级失败隔离。
- [x] 4.3 以 mock 测试实现 akshare fetcher，覆盖行情、个股信息、资金流与字段级失败隔离。
- [x] 4.4 以 TDD 实现 `scripts.fetch_stock_data` 编排层，写入 `stock/<date>/data/<code>.json` 并汇总缺失字段。
- [x] 4.5 自检数据输出不包含真实 token 或异常原文中的 token 字符串。

## 5. Claude Code workflow skill

- [x] 5.1 创建 `.claude/skills/stock-analysis/SKILL.md`，固化股票池分析触发条件与端到端执行序列。
- [x] 5.2 在 skill 中写明来源 A/B/C/未确认分级、当前事实日期要求、Tavily 优先与 WebSearch 回退规则。
- [x] 5.3 在 skill 中写明报告 14 节结构、5 档关注等级、禁止具体交易建议和公司档案保守更新边界。
- [x] 5.4 在 skill 中写明文件完整性、来源完整性、结论边界、Obsidian 兼容和长期档案维护质量门槛。

## 6. 验证与收尾

- [x] 6.1 运行全量 pytest，确认解析、初始化、fetcher、编排和 token 防泄露测试通过。
- [x] 6.2 运行 parse→init 小样本 smoke test，确认目录、模板变量替换和幂等性符合 specs。
- [x] 6.3 按用户选择处理 smoke-test 样例数据，未确认前不提交或保留真实样例输出。
- [x] 6.4 自检未引入 MCP、Web 服务、数据库、任务队列或自定义多 agent 编排。
- [x] 6.5 自检报告模板和 skill 未包含具体买卖价位、仓位、止盈止损等投资建议口径。
