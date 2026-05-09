## 1. 原始数据窗口与落盘

- [x] 1.1 调整 Tushare 结构化底稿抓取，使行情默认限制为最近一年且财务指标保留完整 raw 序列。
- [x] 1.2 调整 akshare 结构化底稿抓取，使行情和资金流默认限制为最近一年。
- [x] 1.3 保持 `stock/<date>/data/<code>.json` 作为 raw JSON 输出，并补齐下游追溯所需来源与状态字段。

## 2. Evidence Pack 生成

- [x] 2.1 新增从 raw JSON 生成 Evidence Pack 的逻辑，禁止生成过程重新联网抓取。
- [x] 2.2 在 Evidence Pack 中写入 `raw_path`、生成时间、数据日期或抓取时间、来源和状态元数据。
- [x] 2.3 对 Evidence Pack 的行情和资金流输出应用最近一年窗口。
- [x] 2.4 对 Evidence Pack 的财务输出实现按任务选择或聚合，禁止整块复制全量财务 raw。

## 3. 默认分析输入与 fixture

- [x] 3.1 调整本地材料索引或路径提示，使默认分析输入指向 Evidence Pack 而不是完整 raw JSON。
- [x] 3.2 增加小型 JSON fixture 或 shape 示例，覆盖 raw 输入、Evidence Pack 输出和缺失字段状态。
- [x] 3.3 更新相关说明或命令输出，明确 raw JSON 仅用于审计、复算和必要回查。

## 4. 验证与收尾

- [x] 4.1 运行 `uv run pytest` 并确认 OpenSpec 语言规则和相关数据流程测试通过。
- [x] 4.2 自检 Claude Code 默认材料未指向完整 raw JSON，且 raw JSON 不会默认进入 prompt。
- [x] 4.3 自检未引入数据库层、因子引擎、完整投研平台或报告模板重写。
- [x] 4.4 自检生成产物未保存 token、`.env` 或本地私密配置。
