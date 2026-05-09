## Why

当前股票数据抓取会保留过大的原始 JSON，尤其是全量历史行情和资金流数据；直接把这些 payload 交给 Claude Code 容易撑大上下文，却不必然提升分析准确性。

本次变更要在保留本地可追溯事实源的前提下，让默认分析输入变成面向任务的小型 Evidence Pack，从而稳定控制上下文并保持可复算。

## What Changes

- 新增 raw-first 的本地数据持久化约定。
- 新增从原始 JSON 派生 Evidence Pack 的默认分析输入能力。
- 修改高频行情与资金流数据的默认抓取和保留窗口为最近一年。
- 新增当前事实元数据约定，覆盖数据日期、抓取时间、来源、状态和原始路径。
- 新增小型 JSON fixture 或 shape 示例用于验证字段结构。

## Capabilities

### New Capabilities

- `evidence-pack`: 定义原始 JSON 与 Evidence Pack 的生成、追溯、默认使用和窗口控制要求。

### Modified Capabilities

- `structured-stock-data-draft`: 调整结构化股票数据草稿的默认数据边界与下游输入契约。

## Impact

- 影响股票数据抓取、落盘、派生摘要和默认分析输入流程。
- 影响现有结构化数据草稿相关脚本、测试 fixture 和 OpenSpec 需求。
- 不引入数据库层、因子引擎或完整投研平台。
