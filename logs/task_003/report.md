# Task 003 — 探索性数据分析（EDA）实现报告

## 实现概述
实现了全套 7 张 EDA 可视化图表，覆盖价格时序、情绪叠加、分布、散点趋势线、分位数收益、累积收益曲线和 Spearman 相关热力图，所有图表均保存为 PNG 并调用 `plt.show()`。

## 主要实现内容
- `plot_price_series()`：图1，HSI 收盘价时序（steelblue 折线）
- `plot_price_vs_sentiment()`：图2，双轴图，左轴收盘价右轴情绪净值，含合并图例
- `plot_sentiment_distribution()`：图3，情绪分布直方图（density=True）+ KDE 叠加
- `plot_sentiment_vs_return()`：图4，情绪 vs 次日收益散点图，含 OLS 趋势线和 r/p 值标注
- `plot_quantile_returns()`：图5，五分位平均收益柱状图（5色区分），含零线
- `plot_cumulative_quantile_returns()`：图6，5 条累积平均收益曲线（按 Q1-Q5 颜色区分）
- `plot_correlation_heatmap()`：图7，7 个特征的 Spearman 相关系数热力图（annot=True，fmt='.3f'）

## 关键代码逻辑
`save_and_show()` 统一封装了 `tight_layout`、`savefig`、`show`、`close` 的调用，避免图形内存泄漏。图6中通过过滤 NaN 并按日期排序后调用 `expanding().mean()` 计算累积平均，而非累积乘积，与 Task spec 保持一致。`validate_columns()` 在主流程中提前校验所有必要列。

## 验收标准完成情况
- [x] 7 张图表全部生成且调用 plt.show() — 已完成
- [x] 图6（Cumulative Average Return by Quantile）有 5 条颜色区分的曲线 — 已完成（使用 QUANTILE_COLORS 列表逐一着色）
- [x] 图4趋势线可见，含 r 和 p 值标注 — 已完成（linregress 计算，标题中嵌入 r/p）
- [x] 图7热力图显示 Spearman 相关系数 — 已完成（corr(method='spearman')，annot=True）
- [x] 全部图表保存 PNG（dpi=150，bbox_inches='tight'）— 已完成

## 输出文件
- `code/task_003_eda.py` — EDA 可视化模块，生成 fig_01 至 fig_07 共 7 张 PNG

<!-- FACTORY:DONE -->
