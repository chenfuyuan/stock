## ADDED Requirements

### Requirement: 触发 A 股投研工作流
系统 SHALL 提供 `stock-analysis` skill，并在用户提供 A 股股票池、请求分析 A 股股票或请求生成每日股票分析文档时作为固定执行流程入口。

#### Scenario: 用户输入股票名称和 A 股代码
- **WHEN** 用户输入包含 `炼石航空(000697.XSHE)` 的股票池并请求分析
- **THEN** Claude Code MUST 使用 `stock-analysis` skill 的执行序列处理该任务

### Requirement: 规定端到端执行序列
`stock-analysis` skill SHALL 规定从解析股票池、确定日期、初始化模板、抓取结构化数据、读取公司档案、联网检索、来源分级、写作日评、保守更新公司档案、生成每日综合文档、更新入口页到质量自检的顺序。

#### Scenario: 执行股票池分析
- **WHEN** skill 处理一个非空股票池
- **THEN** 执行说明 MUST 要求先运行解析脚本，再运行初始化脚本，再运行结构化数据脚本，随后进行联网检索和报告写作

#### Scenario: 股票池为空
- **WHEN** 解析脚本输出空列表
- **THEN** 执行说明 MUST 要求停止并向用户确认输入，而不是继续生成空报告

### Requirement: 强制来源分级与事实边界
`stock-analysis` skill SHALL 要求所有当前事实标注数据日期或检索时间，并按 A/B/C/未确认分级；C 级或未确认来源不能单独支撑核心结论。

#### Scenario: 引用当前事实
- **WHEN** 日评中写入公告、新闻、政策、行情或估值事实
- **THEN** skill 规则 MUST 要求该事实带有来源等级以及数据日期或检索时间

#### Scenario: 只有 C 级来源支持题材线索
- **WHEN** 某核心结论仅由社区讨论、互动平台或市场传闻支持
- **THEN** skill 规则 MUST 要求将其标记为未确认或不足以支撑判断，不能作为核心结论

### Requirement: 强制投研输出边界和质量门槛
`stock-analysis` skill SHALL 要求报告仅输出研究观点，禁止具体买卖价格、仓位、止盈止损，并在完成前检查文件完整性、来源完整性、结论边界、Obsidian 兼容和长期档案维护。

#### Scenario: 完成报告前自检
- **WHEN** Claude Code 准备报告完成
- **THEN** skill 规则 MUST 要求检查每只股票有日评、每日目录有入口页和三份综合文档、每篇日评有来源清单和关注等级、且没有具体买卖价位或仓位建议

### Requirement: 约束联网检索优先级
`stock-analysis` skill SHALL 要求联网检索优先使用 Tavily MCP；当 Tavily 不可用或不适用时，才回退到内置 `WebSearch` 并说明回退。

#### Scenario: Tavily 可用
- **WHEN** 需要检索公告、新闻、政策或行业背景且 Tavily MCP 工具可用
- **THEN** skill 规则 MUST 要求优先使用 Tavily MCP 工具进行搜索或抽取

#### Scenario: Tavily 不可用
- **WHEN** Tavily MCP 工具不可用或不适用
- **THEN** skill 规则 MUST 允许回退到内置 `WebSearch`，并要求在流程记录中说明回退
