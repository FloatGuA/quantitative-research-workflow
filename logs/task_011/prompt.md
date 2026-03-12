# Task 011 — 方法论修正：信号方向反转 + 训练/测试集划分

## 目标

修正研究报告中五项方法论问题（其中问题 4 已修复）：

1. **信号方向反转**：Mean IC 为负（约 -0.108），现有策略做多正情绪，方向与实证结论相反。需将三种策略信号全部取反。
2. **IC 解读去除绝对值**：`insight_dynamic` 和 `task_005_insights.py` 中用 `abs(mean_ic)` 判断预测力强度，隐藏了方向信息。需修正，并在 IC < 0 时明确注明"反向指标"。
3. **显著性 ≠ 方向正确**：报告中 "Statistically significant" 的描述未区分"显著"与"信号方向正确"，需在 insight 文字中补充说明。
4. ✅ 缺失值 ffill → dropna（已修复）
5. **训练/测试集划分**：全部分析均在全样本上进行，特征工程参数（q20/q80、vote_imbalance 中位数）使用未来信息。需引入 80/20 时序划分，所有参数只在训练集上计算，测试集仅用于验证。

## 工作目录

`code/`

## 依赖

- `task_002_feature_engineering.py`（需修改）
- `task_005_insights.py`（需修改）
- `task_006_strategy_design.py`（需修改）
- `task_007_backtest.py`（需修改）
- `create_research_report.py`（需修改：内联代码 cell + insight_dynamic 文本）

---

## 详细要求

### 1. `task_002_feature_engineering.py` — 训练集参数计算

在 `build_sentiment_features` 函数中，添加 `TRAIN_RATIO = 0.8` 常量。`q20`、`q80` 只从前 80% 数据行计算，然后应用到全部数据：

```python
TRAIN_RATIO = 0.8

def build_sentiment_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["sentiment_score"] = df["Up votes"] - df["Down votes"]
    df["vote_imbalance"] = df["sentiment_score"].abs()

    split_n = int(len(df) * TRAIN_RATIO)
    train_sentiment = df["sentiment_score"].iloc[:split_n]

    q80 = train_sentiment.quantile(0.8)
    df["extreme_bull"] = df["sentiment_score"] >= q80

    q20 = train_sentiment.quantile(0.2)
    df["extreme_bear"] = df["sentiment_score"] <= q20

    # 同时输出 split_n 供下游使用，写入常量文件顶部注释即可
    df["is_train"] = False
    df.loc[:split_n - 1, "is_train"] = True
    ...
```

`is_train` 列写入 `hsi_features.csv`，供后续模块使用。

### 2. `task_006_strategy_design.py` — 信号取反 + 训练集中位数

#### 2a. 信号方向全部取反

Strategy A（原：extreme_bull → 1，extreme_bear → -1）改为：
```python
signals.loc[df["extreme_bull"]] = -1   # 极度乐观 → 做空（反向信号）
signals.loc[df["extreme_bear"]] = 1    # 极度悲观 → 做多（反向信号）
```

Strategy B（原：sentiment > threshold → 1）改为：
```python
signals.loc[df["sentiment_score"] > threshold] = -1  # 正情绪 → 做空
signals.loc[df["sentiment_score"] < -threshold] = 1  # 负情绪 → 做多
```

Strategy C 继承 Strategy B 的取反逻辑，另外 `vote_imbalance` 中位数改为只用训练集行计算：
```python
if "is_train" in df.columns:
    median_imbalance = df.loc[df["is_train"], "vote_imbalance"].median()
else:
    median_imbalance = df["vote_imbalance"].median()
```

在所有策略的 docstring 中更新"Economic intuition"，说明这是反向（contrarian）信号：IC 为负，正情绪预示市场过热/超买，做空更合理。

### 3. `task_007_backtest.py` — 分段报告 IS / OOS 绩效

在 `run_all_backtests` 或调用方中，按 `is_train` 列将回测结果切分为两段，分别打印绩效指标表：

```python
def split_and_report(df, results):
    if "is_train" not in df.columns:
        return
    split_date = df.loc[~df["is_train"], "Date"].iloc[0]
    print(f"\nTrain/Test split date: {split_date.date()}")
    for period, mask in [("In-Sample (Train)", df["is_train"]), ("Out-of-Sample (Test)", ~df["is_train"])]:
        idx = df[mask].index
        print(f"\n--- {period} ---")
        period_results = {}
        for key, val in results.items():
            period_portfolio = val["portfolio"].loc[val["portfolio"].index.isin(idx)]
            period_results[key] = {"metrics": calculate_metrics(period_portfolio)}
        print_metrics_table(period_results)
```

在 `main()` 中，在 `run_all_backtests` 后调用 `split_and_report(df, results)`。

### 4. `task_005_insights.py` — 修正 IC 解读

在 `generate_insights` 函数中：

1. 移除 `abs(mean_ic)` 的使用，改为直接用 `mean_ic`：
   ```python
   # 旧
   if abs(mean_ic) > 0.05 and ...
   # 新
   if abs(mean_ic) > 0.05 and ... :
       if mean_ic < 0:
           pred_conclusion = "情绪信号对次日收益具有统计显著的**反向**预测力（IC < 0，为反向指标）..."
       else:
           pred_conclusion = "情绪信号对次日收益具有统计显著的预测力..."
   ```

2. 在 `generate_english_summary` 中，若 `mean_ic < 0`，在 Predictiveness 行后追加一条：
   ```
   - **Signal Direction**: IC < 0 — this is a **contrarian** signal. Positive sentiment predicts negative returns. Strategies should short on high sentiment and go long on low sentiment.
   ```

### 5. `create_research_report.py` — 修正内联代码 + insight_dynamic

#### 5a. insight_dynamic 文本（中英文两版）

在 `TEXTS["insight_dynamic"]` 的英文版和中文版中：

1. 将 `if abs(mean_ic) > 0.02` 改为带方向判断的逻辑：
   ```python
   direction_note = (
       "Note: IC < 0 — this is a **contrarian** signal. "
       "Positive sentiment predicts negative returns; strategies should be inverted."
       if mean_ic < 0 else ""
   )
   ```
2. 在 insight_text 的 "Predictive power" 条目后插入 `direction_note`（如果非空）。
3. 中文版对应修改。

#### 5b. 内联代码 cell 中的特征工程部分

在 notebook 的数据加载/特征工程代码 cell 中，将 `q80 = df["sentiment_score"].quantile(0.8)` 改为：
```python
TRAIN_RATIO = 0.8
split_n = int(len(df) * TRAIN_RATIO)
q80 = df["sentiment_score"].iloc[:split_n].quantile(0.8)
q20 = df["sentiment_score"].iloc[:split_n].quantile(0.2)
df["is_train"] = False
df.loc[:split_n - 1, "is_train"] = True
```

#### 5c. 策略信号 cell 中的取反逻辑

与 task_006 保持一致，极度乐观 → -1，极度悲观 → 1；正情绪 → -1，负情绪 → 1。

#### 5d. 回测结果 cell

在回测结果展示后，增加 IS/OOS 对比表展示（使用 `df["is_train"]` 切分）。

---

## 验收标准

- [ ] `hsi_features.csv` 包含 `is_train` 列，前 80% 为 True
- [ ] `extreme_bull`/`extreme_bear` 分位数基于训练集计算
- [ ] Strategy A/B/C 信号方向已取反（极度乐观 → -1，正情绪 → -1）
- [ ] Strategy C 的 `vote_imbalance` 中位数基于训练集计算
- [ ] `task_007_backtest.py` 打印 IS 和 OOS 两段绩效表
- [ ] `task_005_insights.py` 在 IC < 0 时输出"反向指标"说明
- [ ] `create_research_report.py` 的 `insight_dynamic` 不再使用 `abs(mean_ic)` 判断方向，IC < 0 时有 contrarian 说明
- [ ] Notebook 内联代码与独立模块保持一致
- [ ] `python run.py` 端到端无报错

<!-- FACTORY:TODO -->
