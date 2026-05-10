## MODIFIED Requirements

### Requirement: 编排结构化数据抓取并写入 JSON
系统 SHALL 为每只股票写入 `vault/stock/<date>/data/<code>.json` 原始 JSON，包含股票标识、抓取时间、Tushare 状态、Tushare 记录、akshare 记录和汇总缺失字段，并为下游 Evidence Pack 生成保留可追溯来源信息。

#### Scenario: token 存在时组合两类数据源
- **WHEN** Tushare token 存在且 Tushare 与 akshare mock fetcher 均返回记录
- **THEN** JSON MUST 包含 `tushare_status: ok`、`tushare`、`akshare`，并将各 fetcher 的缺失字段加来源前缀汇总

#### Scenario: token 缺失时跳过 Tushare
- **WHEN** Tushare token 不存在
- **THEN** JSON MUST 包含 `tushare_status: skipped:no_token`、`tushare: null`，且仍尝试写入 akshare 数据

#### Scenario: token 不泄露到输出
- **WHEN** Tushare 调用异常信息中包含真实 token 字符串
- **THEN** 写入的 JSON 文本 MUST 不包含该 token 字符串
