# Task 004 — 信号分析（IC / ICIR / Signal Decay）实现报告

## 实现概述
实现了完整的信号质量评估体系，包括月度 IC 时序计算与可视化、ICIR 计算、全样本 t-test 显著性检验，以及 t+1/t+2/t+3 三期 Signal Decay 分析。

## 主要实现内容
- `compute_monthly_ic()`：按年月分组，对每个月至少 5 条有效数据计算 Spearman IC 和 p-value，返回 ic_df（含 period_dt 时间列）
- `plot_monthly_ic()`：生成图8，绿/红双色柱状图（正/负 IC），叠加均值蓝色虚线
- `print_ic_metrics()`：打印 Mean IC、IC Std、ICIR（处理除零和 NaN）、IC>0 比例、月份数
- `run_ic_ttest()`：调用 `ttest_1samp` 对 IC 序列进行单样本 t-test，打印 t 值和 p 值
- `compute_signal_decay()`：对 lag=1/2/3 分别计算全样本 Spearman IC，支持空样本检测
- `plot_signal_decay()`：生成图9，三色柱状图，IC 值标注在柱上（支持正负方向偏移）
- `save_analysis_tables()`：将 ic_df 和 decay_df 另存为 CSV 供后续使用

## 关键代码逻辑
ICIR 计算中对 `std_ic == 0` 和 NaN 做了防御性处理，返回 `np.nan` 而非 ZeroDivisionError。Signal Decay 通过 `df['return_open'].shift(-lag)` 将未来收益对齐到当期情绪信号，三期衰减曲线量化了信号的时效性。

## 验收标准完成情况
- [x] 月度 IC 时序图生成（绿/红柱状图，蓝色均值虚线）— 已完成
- [x] ICIR 数值正确计算并打印（含 NaN 防护）— 已完成
- [x] Signal Decay 曲线展示 3 个预测期的 IC — 已完成
- [x] t-test 结果打印，含显著性判断（p<0.05）— 已完成
- [x] ic_df 和 decay_df 保存为 CSV — 已完成（超出 spec 要求的增强）

## 输出文件
- `code/task_004_signal_analysis.py` — 信号分析模块，生成 fig_08（月度 IC）和 fig_09（Signal Decay）

<!-- FACTORY:DONE -->
