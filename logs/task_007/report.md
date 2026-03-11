# Task 007 — 回测引擎 实现报告

## 实现概述
实现了纯矢量化回测引擎，对三个策略运行含/不含手续费两个版本（共 6 组回测），计算完整的 8 项绩效指标，并生成 4 张可视化图表。

## 主要实现内容
- `run_backtest()`：矢量化回测核心，信号与 return_open 对齐计算策略日收益，换仓时触发单边手续费（`signal.diff().abs() * fee_rate`），计算累积收益和回撤
- `calculate_metrics()`：计算 Total Return、Annual Return（几何年化）、Annual Volatility、Sharpe Ratio、Max Drawdown、Win Rate（基于 active days）、Total Fee Cost、Num Trades 共 8 项指标，返回格式化字符串字典
- `benchmark_buyhold()`：买入持有基准，使用 return_close，含累积收益和回撤计算
- `run_all_backtests()`：3 策略 × 2 费率 = 6 组，统一调用并打印绩效对比表
- 可视化四张：图10（累积收益，含基准+6条线），图11（回撤曲线），图12（Strategy A 月度热力图），图13（三策略收益分布直方图）
- `ensure_signals()`：若 DataFrame 缺少信号列则自动调用 Task 006 生成

## 关键代码逻辑
回测引擎使用 `(1 + strategy_return).cumprod()` 计算复利累积，用 `cummax()` 替代 `expanding().max()` 计算滚动高点，更 pandas 惯用。手续费仅在 `signal.diff().abs() > 0` 时触发，正确反映换仓成本。Win Rate 分母使用 `(returns != 0).sum()`（active days）而非总天数，避免空仓日稀释胜率。

## 验收标准完成情况
- [x] 3 策略 × 2 版本（含/不含手续费）= 6 组回测全部完成 — 已完成
- [x] 绩效指标表包含所有 8 项指标 — 已完成（格式化打印对比表）
- [x] 4 张可视化图全部生成（fig_10 至 fig_13）— 已完成
- [x] 基准买入持有收益正确计算（close-to-close return）— 已完成

## 输出文件
- `code/task_007_backtest.py` — 回测引擎模块，生成 fig_10 至 fig_13 共 4 张 PNG

<!-- FACTORY:DONE -->
