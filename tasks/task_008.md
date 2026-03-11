# Task 008 — 稳健性检验

## 目标
通过参数敏感性分析、滞后信号检验、去极值分析和滚动 Sharpe，评估策略结论的稳健性。

## 工作目录
`code/`

## 依赖
- `hsi_features.csv`（Task 002 输出）
- 需复用 Task 007 的 `run_backtest` 和 `calculate_metrics` 函数逻辑

## 输出文件
- `task_008_robustness.py` — 稳健性检验模块

## 详细要求

### 1. 阈值敏感性分析（Strategy B）
测试不同阈值下的 Sharpe Ratio：

```python
thresholds = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
sensitivity_results = []

for thresh in thresholds:
    signals = (df['sentiment_score'] > thresh).astype(int) - (df['sentiment_score'] < -thresh).astype(int)
    port = run_backtest(df, signals, fee_rate=0.001)
    metrics = calculate_metrics(port)
    sensitivity_results.append({
        'threshold': thresh,
        'sharpe': float(metrics['Sharpe Ratio']),
        'annual_return': float(metrics['Annual Return'].strip('%')) / 100,
        'max_drawdown': float(metrics['Max Drawdown'].strip('%')) / 100
    })

sens_df = pd.DataFrame(sensitivity_results)
print("Threshold Sensitivity Analysis:")
print(sens_df.to_string(index=False))

# 可视化
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
axes[0].plot(sens_df['threshold'], sens_df['sharpe'], 'bo-')
axes[0].set_title('Sharpe vs Threshold')
axes[1].plot(sens_df['threshold'], sens_df['annual_return'], 'go-')
axes[1].set_title('Annual Return vs Threshold')
axes[2].plot(sens_df['threshold'], sens_df['max_drawdown'], 'ro-')
axes[2].set_title('Max Drawdown vs Threshold')
plt.tight_layout()
plt.savefig('fig_14_sensitivity.png', dpi=150)
plt.show()
```

### 2. 滞后信号检验
使用 lag1/2/3 信号运行相同策略，检验 IC 衰减是否影响策略绩效：

```python
lag_results = []
for lag in [0, 1, 2, 3]:
    if lag == 0:
        score = df['sentiment_score']
    else:
        score = df[f'sentiment_lag{lag}']

    signals = (score > 0.1).astype(int) - (score < -0.1).astype(int)
    port = run_backtest(df, signals, fee_rate=0.001)
    metrics = calculate_metrics(port)
    lag_results.append({'lag': lag, **{k: v for k, v in metrics.items()}})

lag_df = pd.DataFrame(lag_results)
print("\nLag Signal Analysis:")
print(lag_df[['lag', 'Sharpe Ratio', 'Annual Return', 'Max Drawdown']].to_string(index=False))
```

### 3. 去极值后重跑
Winsorize sentiment_score 的 top/bottom 1%，去除极端噪声：

```python
from scipy.stats import mstats

# Winsorize: 裁截 top/bottom 1%
df_win = df.copy()
df_win['sentiment_winsorized'] = mstats.winsorize(df['sentiment_score'].fillna(0), limits=[0.01, 0.01])

signals_win = (df_win['sentiment_winsorized'] > 0.1).astype(int) - \
              (df_win['sentiment_winsorized'] < -0.1).astype(int)

port_original = run_backtest(df, (df['sentiment_score'] > 0.1).astype(int) - (df['sentiment_score'] < -0.1).astype(int), fee_rate=0.001)
port_winsorized = run_backtest(df, signals_win, fee_rate=0.001)

metrics_orig = calculate_metrics(port_original)
metrics_win = calculate_metrics(port_winsorized)

print("\nOutlier Removal Analysis (Strategy B, with fee):")
print(f"{'Metric':<20} {'Original':>12} {'Winsorized':>12}")
for key in ['Sharpe Ratio', 'Annual Return', 'Max Drawdown']:
    print(f"{key:<20} {metrics_orig[key]:>12} {metrics_win[key]:>12}")
```

### 4. 滚动 Sharpe（12 个月窗口）
```python
def rolling_sharpe(portfolio, window=252, annual_factor=252):
    """计算滚动 Sharpe"""
    returns = portfolio['strategy_return']
    roll_mean = returns.rolling(window).mean()
    roll_std = returns.rolling(window).std()
    roll_sharpe = (roll_mean / roll_std) * np.sqrt(annual_factor)
    return roll_sharpe

fig, ax = plt.subplots(figsize=(14, 5))
for name in ['Strategy_A', 'Strategy_B', 'Strategy_C']:
    port = results[f'{name}_no_fee']['portfolio']
    rs = rolling_sharpe(port)
    ax.plot(port['Date'], rs, label=name, alpha=0.8)

ax.axhline(0, color='black', linestyle='--', alpha=0.5)
ax.set_title('Rolling 12-Month Sharpe Ratio')
ax.set_xlabel('Date')
ax.set_ylabel('Sharpe Ratio')
ax.legend()
plt.tight_layout()
plt.savefig('fig_15_rolling_sharpe.png', dpi=150)
plt.show()
```

### 5. 过拟合风险讨论
```python
overfitting_discussion = """
## Overfitting Risk Discussion

1. **In-sample only**: All analysis is performed on the full dataset without out-of-sample validation.
   The results may be optimistic due to data snooping.

2. **Threshold selection**: The ±0.1 threshold for Strategy B was chosen based on visual inspection.
   Sensitivity analysis shows results are relatively stable across thresholds [0.05, 0.2].

3. **Limited history**: 747 trading days (~3 years) is a relatively short period.
   The strategy has not been tested across a full market cycle.

4. **Survivorship bias**: HSI is a market-cap weighted index; constituent changes are not modeled.

5. **Recommendation**: Forward-test the strategy on 2025 data before live deployment.
"""
print(overfitting_discussion)
```

## 代码规范
- 敏感性分析遍历参数列表，结果存入 DataFrame
- 打印格式化对比表
- 过拟合风险以 Markdown 格式输出

## 验收标准
- [ ] 7 个阈值的敏感性分析完成，含可视化
- [ ] lag0/1/2/3 信号对比完成
- [ ] Winsorize 前后对比完成
- [ ] 滚动 Sharpe 图生成（3 条策略曲线）
- [ ] 过拟合风险讨论文字输出

<!-- FACTORY:DONE -->
