## MODIFIED Requirements

### Requirement: 获取 Tushare 结构化底稿
系统 SHALL 使用规范股票代码转换后的 Tushare 代码按本次分析窗口获取股票基础信息、最近一年行情、估值指标和完整财务指标，并在单个接口失败时记录缺失字段而不中断整只股票的数据记录。

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
系统 SHALL 使用去除交易所后缀的 6 位股票代码按本次分析窗口获取最近一年行情、个股信息和资金流，并在单个接口失败时记录缺失字段而不中断整只股票的数据记录。

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
系统 SHALL 为每只股票写入本次分析 run 下的结构化数据文件，包含股票标识、抓取时间、Tushare 状态、Tushare 记录、akshare 记录和汇总缺失字段，并为下游 Evidence Pack 生成保留可追溯来源信息。

#### Scenario: token 存在时组合两类数据源
- **WHEN** Tushare token 存在且 Tushare 与 akshare mock fetcher 均返回记录
- **THEN** JSON MUST 包含 `tushare_status: ok`、`tushare`、`akshare`，并将各 fetcher 的缺失字段加来源前缀汇总

#### Scenario: token 缺失时跳过 Tushare
- **WHEN** Tushare token 不存在
- **THEN** JSON MUST 包含 `tushare_status: skipped:no_token`、`tushare: null`，且仍尝试写入 akshare 数据

#### Scenario: token 不泄露到输出
- **WHEN** Tushare 调用异常信息中包含真实 token 字符串
- **THEN** 写入的 JSON 文本 MUST 不包含该 token 字符串

## ADDED Requirements

### Requirement: 窗口型接口数据按 run 覆盖
系统 SHALL 对 Tushare 和 akshare 可再获取的窗口型数据采用本次分析 run 内整窗重新生成并覆盖的策略，而不是维护本地长期主表或执行增量合并。

#### Scenario: 同一 run 重复生成单股近一年数据
- **WHEN** 在 `2026-05-17` 的分析 run 中再次为 `000697.XSHE` 获取近一年日线和资金流数据
- **THEN** 系统 MUST 覆盖 `data/runs/2026-05-17/000697.XSHE/` 下对应的窗口型数据文件，并保留本次获取时间和查询区间

#### Scenario: 一周后重新分析同一股票
- **WHEN** 在 `2026-05-17` 重新分析曾于 `2026-05-10` 分析过的 `000697.XSHE`
- **THEN** 系统 MUST 为 `2026-05-17` run 重新获取本次分析窗口数据，而不是扫描或增量合并 `2026-05-10` 的历史 run 文件

### Requirement: 限定每日明细采集范围
系统 SHALL 将每日逐股票明细采集限定为目标股票池或对话分析中明确需要补充数据的股票，默认不得采集 A 股全市场每只股票明细。

#### Scenario: 目标股票池分析
- **WHEN** 用户提供只包含 `炼石航空(000697.XSHE)` 的目标股票池并请求分析
- **THEN** 系统 MUST 只为该目标股票池及分析中明确追加的股票获取逐股票明细数据

#### Scenario: 需要同行对比
- **WHEN** 分析过程明确需要补充同行公司作为对比样本
- **THEN** 系统 MUST 仅为被选定的同行公司获取本次问题所需的字段和时间窗口

### Requirement: 保存每日市场汇总快照
系统 SHALL 支持将小体量每日市场汇总数据保存为复盘证据快照，包括指数、总成交额、涨跌家数、涨跌停统计和行业/概念汇总。

#### Scenario: 生成每日市场汇总 raw
- **WHEN** 系统采集 `2026-05-10` 的市场汇总数据
- **THEN** 系统 MUST 将汇总数据保存到 `vault/raw/data/market-summary/2026-05-10/`，并写入包含数据源、采集时间、交易日和字段口径的 metadata

#### Scenario: 汇总数据不包含逐股票明细
- **WHEN** 系统保存每日市场汇总 raw
- **THEN** 输出文件 MUST 不包含全 A 逐股票行情、全市场资金流、分钟线或逐笔明细
