## ADDED Requirements

### Requirement: 沉淀研究结论与证据
系统 SHALL 在生成的研究页面中提供用于记录研究结论、证据来源和数据日期的结构，使研究判断可以在未来被追溯。

#### Scenario: 日评包含证据沉淀区域
- **WHEN** 生成个股日评 Markdown 文件
- **THEN** 文件 MUST 包含记录研究结论、证据来源和数据日期的章节或链接入口

#### Scenario: 证据记录保留来源边界
- **WHEN** 生成证据相关 Markdown 页面或章节
- **THEN** 内容 MUST 包含提示用户填写来源、发布日期或检索时间的字段或占位文本

### Requirement: 沉淀后续验证点
系统 SHALL 在研究页面中提供后续验证点记录结构，使用户能够记录未来需要验证的经营、财务、政策、产业或事件线索。

#### Scenario: 日评包含后续验证点
- **WHEN** 生成个股日评 Markdown 文件
- **THEN** 文件 MUST 包含后续验证点章节或指向复盘入口的 wikilink

#### Scenario: 研究日志承接验证点
- **WHEN** 生成每日研究日志 Markdown 文件
- **THEN** 文件 MUST 包含可汇总当日验证点、待跟踪问题或后续观察事项的章节骨架

### Requirement: 支持复盘记录
系统 SHALL 提供复盘入口，使用户能够回看历史判断是否被证实、证伪或仍待观察。

#### Scenario: 生成复盘入口
- **WHEN** 初始化任意日期的分析目录
- **THEN** 系统 MUST 生成或保留复盘入口 Markdown 页面，并包含历史判断、验证结果和后续处理的章节骨架
