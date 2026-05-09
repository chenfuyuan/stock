## ADDED Requirements

### Requirement: 从原始 JSON 生成 Evidence Pack
系统 SHALL 先保存原始 JSON 作为本地事实源，再从该原始 JSON 派生 Evidence Pack；Evidence Pack 的生成 MUST 不依赖重新联网抓取。

#### Scenario: 原始 JSON 可复算 Evidence Pack
- **WHEN** 给定已落盘的原始 JSON 路径并执行 Evidence Pack 生成
- **THEN** 系统 MUST 从该原始 JSON 生成 Evidence Pack，且不调用外部网络数据源

#### Scenario: Evidence Pack 记录原始路径
- **WHEN** Evidence Pack 生成成功
- **THEN** 输出 MUST 包含指向原始 JSON 的 `raw_path`

### Requirement: Evidence Pack 携带当前事实元数据
系统 SHALL 在 Evidence Pack 中记录可追溯元数据，至少包含生成时间、数据日期或抓取时间、来源和状态信息。

#### Scenario: 元数据完整写入
- **WHEN** 输入 raw JSON 包含数据日期、抓取时间、来源和状态字段
- **THEN** Evidence Pack MUST 保留生成时间、数据日期或抓取时间、来源和状态信息

#### Scenario: 数据源缺失状态可见
- **WHEN** raw JSON 中某个数据源被跳过或存在缺失字段
- **THEN** Evidence Pack MUST 暴露对应状态或缺失字段信息

### Requirement: 默认分析输入使用 Evidence Pack
系统 SHALL 将 Evidence Pack 作为 Claude Code 默认读取的分析输入，不得默认把完整原始 JSON 作为 prompt 或输入材料。

#### Scenario: 默认材料指向 Evidence Pack
- **WHEN** 生成股票分析所需的本地材料索引或路径提示
- **THEN** 默认输入路径 MUST 指向 Evidence Pack 而不是完整原始 JSON

### Requirement: 高频数据使用一年窗口
系统 SHALL 在 Evidence Pack 中默认只包含最近一年行情、资金流等高频数据。

#### Scenario: 行情数据被窗口化
- **WHEN** raw JSON 中包含超过一年的日频行情数据
- **THEN** Evidence Pack 中的行情数据 MUST 只包含最近一年窗口内的记录

#### Scenario: 资金流数据被窗口化
- **WHEN** raw JSON 中包含超过一年的资金流数据
- **THEN** Evidence Pack 中的资金流数据 MUST 只包含最近一年窗口内的记录

### Requirement: 财务数据按任务选择或聚合
系统 SHALL 允许原始 JSON 保留完整财务历史，但 Evidence Pack MUST 只包含按分析任务选择或聚合后的财务数据，不得整块复制全量财务原始数据。

#### Scenario: 财务原始历史不被整块复制
- **WHEN** raw JSON 中包含多期完整财务指标序列
- **THEN** Evidence Pack MUST 输出选定字段、关键期数或聚合结果，而不是完整财务原始记录列表
