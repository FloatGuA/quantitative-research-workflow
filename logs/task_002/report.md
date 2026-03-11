# Task 002 — 收益率构建与情绪特征工程 实现报告

## 实现概述
基于 `hsi_clean.csv` 构建了所有下游分析所需的收益率序列（`return_open`、`return_close`）与情绪特征（7 个），并通过 `pd.qcut` 生成五分位情绪分组，最终保存 `hsi_features.csv`。

## 主要实现内容
- `build_returns()`：`return_open = Open.shift(-1) / Open - 1`（次日开盘收益，避免收盘价反转偏差）；`return_close = Close.pct_change()`（收盘到收盘收益用于对比）
- `build_sentiment_features()`：计算 `sentiment_score`、`vote_imbalance`、`extreme_bull`（>=q80）、`extreme_bear`（<=q20）及三个滞后信号 `sentiment_lag1/2/3`
- `build_sentiment_quantiles()`：使用 `rank(method='first')` 后 `pd.qcut` 分 5 等组，避免重复值问题
- `print_feature_diagnostics()`：打印特征统计摘要、extreme_bull/bear 天数、五分位分布
- `validate_columns()`：前置列校验保障依赖完整性

## 关键代码逻辑
`return_open` 使用 `shift(-1)` 对齐次日开盘价，确保信号在 t 日生成、t+1 日执行，无未来信息泄漏。情绪分位数通过 `rank(method='first')` 先对 sentiment_score 排名再切分，避免 `pd.qcut` 因重复值导致的分组失败。

## 验收标准完成情况
- [x] return_open 使用 shift(-1)，无未来信息泄漏 — 已完成
- [x] 7 个情绪特征全部计算（sentiment_score、vote_imbalance、extreme_bull、extreme_bear、lag1/2/3）— 已完成
- [x] extreme_bull/bear 各约 20% 的行被标记（基于 q80/q20 分位数）— 已完成
- [x] sentiment_quantile 五分组分布均匀（rank 后 qcut 保障）— 已完成
- [x] hsi_features.csv 成功保存 — 已完成

## 输出文件
- `code/task_002_feature_engineering.py` — 特征工程模块，含完整验证与诊断输出

<!-- FACTORY:DONE -->
