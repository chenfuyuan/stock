## ADDED Requirements

### Requirement: 读取本地 Tushare token
系统 SHALL 从项目根目录 `.env` 或环境变量 `TUSHARE_TOKEN` 读取 Tushare token；当两者均不存在时返回无 token 状态。

#### Scenario: `.env` 优先于环境变量
- **WHEN** `.env` 中存在 `TUSHARE_TOKEN=from-dotenv` 且环境变量中存在 `TUSHARE_TOKEN=from-env-var`
- **THEN** token 读取结果 MUST 为 `from-dotenv`

#### Scenario: token 缺失
- **WHEN** `.env` 与环境变量均未提供 `TUSHARE_TOKEN`
- **THEN** token 读取结果 MUST 为 `None`

### Requirement: 获取 Tushare 结构化底稿
系统 SHALL 使用规范股票代码转换后的 Tushare 代码获取股票基础信息、最近一年行情、估值指标和完整财务指标，并在单个接口失败时记录缺失字段而不中断整只股票的数据记录。

#### Scenario: Tushare 多接口成功
- **WHEN** Tushare mock client 返回基础信息、行情、估值和财务指标 DataFrame
- **THEN** 输出记录 MUST 包含 `source: tushare`、原规范代码、数据日期、各字段数据和空的 `missing_fields`

#### Scenario: Tushare 行情限制为最近一年
- **WHEN** Tushare mock client 返回超过一年的日频行情 DataFrame
- **THEN** 输出记录中的行情数据 MUST 只包含最近一年窗口内的记录

#### Scenario: Tushare 单接口失败
- **WHEN** Tushare 财务指标接口抛出异常但其他接口成功
- **THEN** 输出记录 MUST 将 `fina_indicator` 置为空，并在 `missing_fields` 中记录 `fina_indicator`

### Requirement: 获取 akshare 结构化底稿
系统 SHALL 使用去除交易所后缀的 6 位股票代码获取最近一年行情、个股信息和资金流，并在单个接口失败时记录缺失字段而不中断整只股票的数据记录。

#### Scenario: akshare 多接口成功
- **WHEN** akshare mock 接口返回行情、个股信息和资金流 DataFrame
- **THEN** 输出记录 MUST 包含 `source: akshare`、原规范代码、数据日期、三类字段数据和空的 `missing_fields`

#### Scenario: akshare 高频数据限制为最近一年
- **WHEN** akshare mock 接口返回超过一年的行情或资金流 DataFrame
- **THEN** 输出记录中的行情和资金流数据 MUST 只包含最近一年窗口内的记录

#### Scenario: akshare 单接口失败
- **WHEN** akshare 资金流接口抛出异常但其他接口成功
- **THEN** 输出记录 MUST 将 `fund_flow` 置为空，并在 `missing_fields` 中记录 `fund_flow`

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
