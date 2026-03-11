# Task 006 — 策略设计 代码审查报告

## 总体评价
Pass — 三个策略实现完整，经济直觉说明详尽，参数化设计良好，信号覆盖诊断超出 spec 要求。

## Must Fix（必须修复）
- 无

## Should Fix（建议修复）
- Docstring 中提到"Backtests should shift the final signal by one period before trading"，但实际信号并未在此模块中 shift，这个对齐责任转移给了调用方（Task 007）。需确认 Task 007 回测引擎确实正确处理了对齐，否则存在隐式前视偏差风险。建议在 docstring 中更明确地说明当前模块的信号含义（t 日已知信息 → 预测 t+1 日收益），由 backtest 使用 `signal * return_open` 对齐
- Strategy C 的 `median_imbalance` 基于全样本计算，存在轻微前视偏差（在真实回测中中位数应为滚动或截至当日的历史中位数）

## Nice to Have（可选优化）
- `strategy_c_signals()` 内部调用了 `strategy_b_signals()`，会重复打印一次 Strategy B 的信号分布，导致日志输出冗余；可通过传入 `verbose=False` 参数控制
- `SIGNAL_COLUMNS = ["signal_a", "signal_b", "signal_c"]` 作为模块常量设计良好，便于 Task 007 直接引用

## 代码质量评估
- **可读性**: 优秀 — 每个策略函数名称、docstring 和 Timing note 清晰，`_print_signal_distribution` 私有辅助函数复用良好
- **正确性**: 良好 — 信号值域 {-1, 0, 1} 正确；`.where()` 过滤逻辑正确；但全样本中位数过滤存在轻微前视偏差
- **完整性**: 优秀 — 三个策略全部实现，validate_columns 提前保障，信号覆盖诊断完备

## 审查结论
Pass

<!-- FACTORY:DONE -->
