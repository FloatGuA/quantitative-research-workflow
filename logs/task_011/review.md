# Task 011 Review

## 审查结论

**Pass with Warnings**

核心改动全部正确实现，方法论问题已修复。两项非阻塞性警告见下。

---

## Must Fix（阻塞性问题）

无。

---

## Should Fix（建议修复）

### W1 — `build_sentiment_quantiles` 仍使用全样本 qcut

**位置**：`task_002_feature_engineering.py` `build_sentiment_quantiles()`

`sentiment_quantile` 列通过全样本 `pd.qcut` 计算，仍存在轻微全样本泄露。该列仅用于 EDA 图表（分位数收益对比），**不影响策略信号或回测**，但严格意义上应改为训练集分位数边界。

**建议**：优先级低，可在后续迭代修复。

### W2 — OOS 回测起始仓位可能不干净

**位置**：`task_007_backtest.py` `split_and_report()` / `_rebase_portfolio()`

切分 OOS 段时，若训练集最后一日持有仓位，OOS 第一日的 `strategy_return` 可能来自前一日信号，导致 OOS 第一笔收益实为 IS 末尾的续仓收益。当前 `_rebase_portfolio` 只重算路径统计量，不处理起始仓位归零。

**建议**：在 `split_and_report` 中将 OOS `portfolio` 的第一行 `strategy_return` 强制置零后再 rebase，或在说明中注明该限制。优先级中等。

---

## 验收标准核查

| # | 验收标准 | 状态 |
|---|---------|------|
| 1 | `hsi_features.csv` 包含 `is_train` 列，前 80% 为 True | ✅ |
| 2 | `extreme_bull`/`extreme_bear` 分位数基于训练集计算 | ✅ 第 48/54-55 行 |
| 3 | Strategy A/B/C 信号方向已取反 | ✅ extreme_bull→-1，正情绪→-1 |
| 4 | Strategy C 的 `vote_imbalance` 中位数基于训练集计算 | ✅ `df.loc[df["is_train"]]` |
| 5 | `task_007_backtest.py` 打印 IS 和 OOS 两段绩效表 | ✅ `split_and_report()` |
| 6 | `task_005_insights.py` IC < 0 时输出"反向指标"说明 | ✅ |
| 7 | `create_research_report.py` insight_dynamic IC < 0 有 contrarian 说明 | ✅ `direction_note` 变量 |
| 8 | Notebook 内联代码与独立模块保持一致 | ✅ |
| 9 | `python run.py` 端到端无报错 | ✅ 两个 notebook 执行无 error cell |

---

## 方法论正确性检查

1. **q80/q20 仅在训练行计算** ✅ — `train_sentiment = df["sentiment_score"].iloc[:split_n]`，然后 `q80 = train_sentiment.quantile(0.8)`。索引为 RangeIndex，`.loc[:split_n-1]` 与 `.iloc[:split_n]` 等价，无越界风险。

2. **三种策略信号全部取反** ✅ — Strategy A: `extreme_bull→-1, extreme_bear→1`；Strategy B: `>threshold→-1, <-threshold→1`；Strategy C 继承 B 的取反逻辑。Docstring 已更新为 contrarian 经济含义。

3. **vote_imbalance 中位数基于训练集** ✅ — `is_train` 列存在时使用 `df.loc[df["is_train"], "vote_imbalance"].median()`，兜底 fallback 为全样本中位数（当列不存在时）。

4. **IS/OOS 分段绩效输出** ✅ — `split_and_report()` 按 `is_train` mask 切片，`_rebase_portfolio()` 重算路径统计量，两段独立报告。

5. **task_005 不再用 abs() 隐藏方向** ✅ — `abs(mean_ic)` 仅用于预测力强度阈值判断（合理），方向判断由独立的 `if mean_ic < 0` 分支处理，IC < 0 时中英文均输出明确的反向指标说明。

6. **create_research_report.py 与独立模块一致** ✅ — 特征工程 cell 同步了 `TRAIN_RATIO`、`split_n`、`is_train` 逻辑；策略 cell 同步了信号取反；回测 cell 新增 `split_metrics` 函数和 IS/OOS 对比表展示。
