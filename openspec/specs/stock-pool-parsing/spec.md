## ADDED Requirements

### Requirement: 解析股票池输入
系统 SHALL 将用户粘贴的 A 股股票池文本解析为按输入顺序排列的股票记录列表，每条记录包含 `name` 与规范化后的 `code`。

#### Scenario: 解析带括号的编号列表
- **WHEN** 输入包含 `1. 炼石航空(000697.XSHE)` 与 `2. 甘肃能源(000791.XSHE)`
- **THEN** 输出为包含 `{"name": "炼石航空", "code": "000697.XSHE"}` 与 `{"name": "甘肃能源", "code": "000791.XSHE"}` 的 JSON 列表

#### Scenario: 跳过没有股票代码的行
- **WHEN** 输入包含标题、注释或其他没有 6 位代码和交易所后缀的行
- **THEN** 输出中 MUST 不包含这些无效行对应的记录

### Requirement: 规范化 A 股代码后缀
系统 SHALL 将支持的 A 股代码后缀规范化为 `.XSHE`、`.XSHG` 或 `.XBSE`，并支持转换为 Tushare 使用的 `.SZ`、`.SH` 或 `.BJ` 后缀。

#### Scenario: 将 Tushare 后缀转换为规范后缀
- **WHEN** 输入代码为 `000697.SZ`、`600000.SH` 或 `430489.BJ`
- **THEN** 规范化结果分别为 `000697.XSHE`、`600000.XSHG` 与 `430489.XBSE`

#### Scenario: 转换为 Tushare 代码
- **WHEN** 规范化代码为 `000697.XSHE`、`600000.XSHG` 或 `430489.XBSE`
- **THEN** Tushare 代码分别为 `000697.SZ`、`600000.SH` 与 `430489.BJ`

### Requirement: 按股票代码去重
系统 SHALL 按规范化后的股票代码去重，并保留同一代码第一次出现的记录。

#### Scenario: 同一股票用不同后缀重复出现
- **WHEN** 输入同时包含 `炼石航空(000697.XSHE)` 与 `炼石航空 000697.SZ`
- **THEN** 输出列表中 MUST 只包含第一条 `000697.XSHE` 记录
