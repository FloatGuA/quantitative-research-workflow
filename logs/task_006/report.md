# Task 006 — 策略设计 实现报告

## 实现概述
实现了三个量化交易策略函数（Strategy A/B/C），每个函数含完整经济直觉 docstring，并通过 `generate_all_signals()` 统一生成信号并输出信号分布和相关性统计。

## 主要实现内容
- `strategy_a_signals()`：Long-Short Portfolio，做多 extreme_bull（top 20%），做空 extreme_bear（bottom 20%），其余空仓
- `strategy_b_signals()`：Threshold Strategy，sentiment_score > threshold（默认 0.1）做多，< -threshold 做空，中性区间空仓，threshold 参数化
- `strategy_c_signals()`：Volume Filter Strategy，在 Strategy B 基础上叠加 vote_imbalance >= 中位数的过滤条件，高共识时执行信号
- `generate_all_signals()`：依次调用三个策略函数，输出信号分布、信号相关性矩阵，以及 Strategy C 相对 B 的有效信号减少比例
- `_print_signal_distribution()`：私有辅助函数统一打印 Long/Short/Hold 天数和比例

## 关键代码逻辑
Strategy C 通过 `base_signals.where(high_conviction, other=0)` 实现过滤，高效且无循环。`generate_all_signals()` 额外计算并打印 `reduction_ratio = 1 - effective_c / effective_b`，定量验证 Strategy C 对有效信号的削减程度（预期约 50%）。

## 验收标准完成情况
- [x] 三个策略函数均已实现，签名清晰 — 已完成
- [x] Strategy A 约 20% long + 20% short + 60% hold（基于 q80/q20 分位数阈值）— 已完成
- [x] Strategy C 比 Strategy B 的有效信号数约减少 50%（通过中位数过滤）— 已完成（reduction_ratio 打印验证）
- [x] 每个策略有完整经济直觉 docstring — 已完成（英文 docstring 含 Economic intuition 和 Timing note）

## 输出文件
- `code/task_006_strategy_design.py` — 策略定义模块，信号作为 Series 返回，供 Task 007 回测引擎调用

<!-- FACTORY:DONE -->
