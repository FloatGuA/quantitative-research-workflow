# Task 007 — 回测引擎 代码审查报告

## 总体评价
Pass — 回测引擎矢量化实现完整，绩效指标计算准确，可视化覆盖全面，且有空结果防护。

## Must Fix（必须修复）
- 无

## Should Fix（建议修复）
- `run_backtest()` 中将信号与 return_open 直接相乘（`signal * return_open`），此处 return_open 已经是 t+1 日的收益（由 Task 002 的 shift(-1) 生成），所以信号对齐是正确的。但这个依赖关系完全隐式，建议在函数文档字符串中明确说明"假设 return_open 已预先向前对齐（shift(-1)）"，否则使用者可能误用普通当日收益列
- `calculate_metrics()` 中 Sharpe Ratio 假设无风险利率为 0，建议在文档或注释中说明，便于研究报告引用

## Nice to Have（可选优化）
- `plot_monthly_heatmap()` 中 `resample("ME")` 使用了月末频率，若 pandas 版本不同（旧版用 "M"），可能引发警告；当前实现是正确的，但可加版本注释
- 绩效指标在 `calculate_metrics()` 中返回格式化字符串，在 Task 008 的稳健性分析中需要通过 `parse_percent()`/`parse_float()` 反解析，造成额外开销；可考虑同时返回原始数值版本

## 代码质量评估
- **可读性**: 优秀 — 函数职责清晰，常量统一定义，绩效表格打印格式专业
- **正确性**: 优秀 — 手续费触发逻辑正确（换仓触发）；Win Rate 使用 active days 分母合理；drawdown 用 cummax 计算高效
- **完整性**: 优秀 — 6 组回测、8 项指标、4 张图全部完成，`ensure_signals` 兜底设计健壮

## 审查结论
Pass

<!-- FACTORY:DONE -->
