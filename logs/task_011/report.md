# Task 011 实现报告 — 方法论修正：信号方向反转 + 训练/测试集划分

**日期**：2026-03-12

---

## 1. 实现摘要

- **训练/测试集划分**：在 `task_002_feature_engineering.py` 中引入 `TRAIN_RATIO = 0.8` 常量，`q80`/`q20` 分位数阈值仅在前 80% 的训练行上计算，并新增 `is_train` 布尔列写入 `hsi_features.csv`，供所有下游模块使用。
- **信号方向全面取反**：`task_006_strategy_design.py` 中三种策略均已修正为反向（contrarian）逻辑：极度乐观映射至 -1（做空），极度悲观映射至 +1（做多）；正情绪同样映射至 -1。Strategy C 的 `vote_imbalance` 中位数改为仅在训练集行上计算，消除前视偏差。
- **IC 解读修正**：`task_005_insights.py` 移除了对 `abs(mean_ic)` 的依赖，改为直接判断 IC 方向；IC < 0 时在中文和英文 insight 中均明确注明"反向指标"，并在英文摘要中新增 `Signal Direction` 条目。
- **IS/OOS 分段报告**：`task_007_backtest.py` 新增 `split_and_report()` 函数和 `_rebase_portfolio()` 辅助函数，在全样本绩效表之后自动打印"In-Sample (Train)"与"Out-of-Sample (Test)"两张独立绩效表，并重新基准化各子段的累计收益和回撤。
- **Notebook 内联代码同步**：`create_research_report.py` 中特征工程 cell、策略信号 cell 及回测结果 cell 全部与独立模块保持一致，包括训练集参数计算逻辑、信号取反逻辑，以及 IS/OOS 对比表展示。`insight_dynamic` 文本（中英文两版）均已加入 `direction_note` 变量，IC < 0 时输出 contrarian 提示。

---

## 2. 各文件改动说明

### task_002_feature_engineering.py

- 文件顶部新增模块级常量 `TRAIN_RATIO = 0.8`。
- `build_sentiment_features()` 函数内：
  - 计算 `split_n = int(len(df) * TRAIN_RATIO)`。
  - 从 `df["sentiment_score"].iloc[:split_n]` 提取训练集情绪序列，分别计算 `q80`（0.8 分位数）和 `q20`（0.2 分位数），再应用到全部行生成 `extreme_bull` / `extreme_bear`。
  - 新增 `is_train` 列，前 `split_n` 行置为 `True`，其余置为 `False`。
- `print_feature_diagnostics()` 新增打印训练/测试观测量统计。

### task_005_insights.py

- `generate_insights()` 函数：判断 IC 强度的条件保留 `abs(mean_ic)` 用于量级比较，但方向描述改为在 `mean_ic < 0` / `mean_ic >= 0` 两条分支下分别输出中文"反向预测力（IC < 0，为反向指标）"或正向预测力说明，并补充"统计显著 ≠ 方向正确"的注意事项。
- 信号稳定性段落（第 4 点）：当 `mean_ic < 0` 时，改为统计负 IC 月份占比以配合反向信号语义。
- `generate_english_summary()`：当 `mean_ic < 0` 时，在 Predictiveness 行之后插入 `Signal Direction` 条目，说明策略应在高情绪时做空、低情绪时做多。
- `build_markdown_content()`：新增 `trading_note` 变量，IC < 0 时在交易含义部分加入 contrarian 方向说明。

### task_006_strategy_design.py

- `strategy_a_signals()`：`extreme_bull` → `-1`，`extreme_bear` → `+1`；docstring 更新 Economic intuition 说明 IC 为负、做反向操作的逻辑依据。
- `strategy_b_signals()`：`sentiment_score > threshold` → `-1`，`sentiment_score < -threshold` → `+1`；docstring 同步更新。
- `strategy_c_signals()`：继承 Strategy B 的取反逻辑；`median_imbalance` 优先从 `df.loc[df["is_train"], "vote_imbalance"]` 计算，若 `is_train` 列不存在则回退到全样本中位数；docstring 说明训练集过滤器的理由。

### task_007_backtest.py

- 新增辅助函数 `_rebase_portfolio(portfolio)`：对子段 DataFrame 重新计算累计收益和回撤，避免继承全样本路径依赖。
- 新增 `split_and_report(df, results)` 函数：检测 `is_train` 列，确定切分日期，对 In-Sample 和 Out-of-Sample 分别截取各策略 portfolio、调用 `_rebase_portfolio()` 再调用 `calculate_metrics()`，最后复用 `print_metrics_table()` 输出。
- `main()` 在 `run_all_backtests(df)` 后立即调用 `split_and_report(df, results)`。

### create_research_report.py

- **特征工程 cell**（约第 514 行）：`TRAIN_RATIO = 0.8`、`split_n` 计算、基于训练集的 `q80`/`q20`、`is_train` 列创建，与 task_002 保持一致。
- **`insight_dynamic` 文本**（英文版约第 290 行，中文版约第 326 行）：两版均新增 `direction_note` 变量，当 `mean_ic < 0` 时输出 contrarian 说明，并插入到 Predictive power 条目之后。
- **策略信号 cell**（约第 1206 行）：Strategy A `extreme_bull` → `-1`、`extreme_bear` → `+1`；Strategy B/C `sentiment_score > threshold` → `-1`、`sentiment_score < -threshold` → `+1`；Strategy C 的中位数从 `is_train` 行计算。
- **回测结果 cell**（约第 688 行）：新增内联 `split_metrics()` 和 `rebase_portfolio()` 函数，在全样本绩效表之后展示 IS/OOS 对比表，并标注切分日期。

---

## 3. 验收标准逐条核对

| 验收标准 | 状态 | 说明 |
|---|---|---|
| `hsi_features.csv` 包含 `is_train` 列，前 80% 为 True | ✅ 通过 | task_002 `build_sentiment_features()` 已新增 `is_train` 列并写入 CSV |
| `extreme_bull`/`extreme_bear` 分位数基于训练集计算 | ✅ 通过 | `q80`/`q20` 均从 `iloc[:split_n]` 子集取分位数 |
| Strategy A/B/C 信号方向已取反（极度乐观 → -1，正情绪 → -1） | ✅ 通过 | task_006 三个策略函数均已取反；create_research_report.py 内联 cell 同步 |
| Strategy C 的 `vote_imbalance` 中位数基于训练集计算 | ✅ 通过 | 优先用 `df.loc[df["is_train"], "vote_imbalance"].median()`，两处（task_006 + create_research_report.py）均已修改 |
| `task_007_backtest.py` 打印 IS 和 OOS 两段绩效表 | ✅ 通过 | `split_and_report()` 已实现并在 `main()` 中调用 |
| `task_005_insights.py` 在 IC < 0 时输出"反向指标"说明 | ✅ 通过 | 中英文 insight 均在 IC < 0 分支下输出反向信号说明 |
| `create_research_report.py` 的 `insight_dynamic` 不再依赖 `abs(mean_ic)` 判断方向，IC < 0 时有 contrarian 说明 | ✅ 通过 | `direction_note` 变量已插入中英文两版 `insight_dynamic` |
| Notebook 内联代码与独立模块保持一致 | ✅ 通过 | 特征工程、策略信号、回测结果三处 cell 均与对应独立模块对齐 |
| `python run.py` 端到端无报错 | ⚠️ 未验证 | 本报告不执行代码；需在有 HSI.xlsx 的环境中手动验证 |

---

## 4. 已知风险 / 注意事项

1. **`calculate_metrics()` 仍返回格式化字符串**：task_007 的 `calculate_metrics()` 返回值为 `"12.34%"` 格式的字符串，`split_and_report()` 和 `create_research_report.py` 内联 cell 均直接展示该字符串，无数值比较需求，因此本次未拆分为 float + 格式化层。若 task_008 稳健性检验需要数值对比，仍需后续修正（CLAUDE.md Should Fix 第 3 项）。

2. **`task_005` 的模块导入依赖未解决**：`task_005_insights.py` 仍通过 `from task_004_signal_analysis import ...` 导入，在 Jupyter Notebook 中直接运行时可能因工作目录问题失败（CLAUDE.md Should Fix 第 1 项）。本次修改未涉及该问题。

3. **IS/OOS 仅单次切分**：80/20 时序切分是单次验证，未做 walk-forward 检验，过拟合风险已在 `create_research_report.py` 的 `overfitting_md` 文本中说明。

4. **`run.py` 未在修改范围内**：验收标准中的端到端运行依赖 `run.py`，其调用链（task_002 → task_006 → task_007）需在实际数据环境下验证信号取反和 IS/OOS 表输出是否正常。
