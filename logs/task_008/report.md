# Task 008 — 稳健性检验 实现报告

## 实现概述
实现了四个维度的稳健性检验：阈值敏感性分析（7 个阈值）、滞后信号对比（lag 0-3）、去极值（Winsorize）前后对比，以及滚动 12 个月 Sharpe 分析，并输出过拟合风险讨论。

## 主要实现内容
- `threshold_sensitivity_analysis()`：遍历 7 个阈值（0.0 至 0.3），运行含手续费回测，记录 Sharpe、Annual Return、Max Drawdown，生成图14（三子图折线图），使用 `parse_percent()`/`parse_float()` 解析格式化字符串
- `lag_signal_analysis()`：对 lag=0/1/2/3 分别生成 ±0.1 阈值信号，运行含手续费回测，对比 Sharpe/Return/Drawdown 四组结果
- `outlier_removal_analysis()`：使用 `scipy.stats.mstats.winsorize` 裁截 top/bottom 1% 的极端情绪值，对比原始与去极值后的绩效
- `rolling_sharpe()`：计算 252 日滚动 Sharpe（rolling mean/std * sqrt(252)），`plot_rolling_sharpe()` 绘制三策略曲线（图15）
- `build_strategy_results()`：单独构建无手续费回测结果用于滚动 Sharpe 图
- `print_overfitting_discussion()`：打印五点过拟合风险讨论（Markdown 格式）

## 关键代码逻辑
`parse_percent()` 和 `parse_float()` 辅助函数专门处理 Task 007 返回的格式化字符串，将 "12.34%" 转换为 0.1234 等数值供稳健性分析使用。滚动 Sharpe 使用单独的无手续费结果，与实际回测结果分离，避免手续费对滚动窗口的干扰。

## 验收标准完成情况
- [x] 7 个阈值的敏感性分析完成，含三子图可视化（图14）— 已完成
- [x] lag0/1/2/3 信号对比完成（对比表打印）— 已完成
- [x] Winsorize 前后对比完成（三项指标对比表）— 已完成
- [x] 滚动 Sharpe 图生成（3 条策略曲线，图15）— 已完成
- [x] 过拟合风险讨论文字输出 — 已完成（5 条 Markdown 格式风险说明）

## 输出文件
- `code/task_008_robustness.py` — 稳健性检验模块，生成 fig_14（敏感性）和 fig_15（滚动 Sharpe）

<!-- FACTORY:DONE -->
