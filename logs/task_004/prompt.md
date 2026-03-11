# Task 004 — 信号分析（IC / ICIR / Signal Decay）

## 目标
通过 IC 时序分析、ICIR 计算和 Signal Decay Test 量化评估情绪信号的预测能力。

## 工作目录
`code/`

## 依赖
- `hsi_features.csv`（Task 002 输出）

## 输出文件
- `task_004_signal_analysis.py` — 信号分析模块

## 详细要求

### 1. 月度 IC 计算与时序图
IC（Information Coefficient）= Spearman 相关系数（情绪信号与下一期收益）

```python
from scipy import stats

# 按月计算 IC
df['year_month'] = df['Date'].dt.to_period('M')
monthly_ic = []

for period, group in df.groupby('year_month'):
    clean = group[['sentiment_score', 'return_open']].dropna()
    if len(clean) < 5:  # 数据量不足跳过
        continue
    ic, p = stats.spearmanr(clean['sentiment_score'], clean['return_open'])
    monthly_ic.append({'period': period, 'ic': ic, 'p_value': p, 'n': len(clean)})

ic_df = pd.DataFrame(monthly_ic)
ic_df['period_dt'] = ic_df['period'].dt.to_timestamp()

# IC 时序图
fig, ax = plt.subplots(figsize=(14, 5))
ax.bar(ic_df['period_dt'], ic_df['ic'], width=20,
       color=['green' if x > 0 else 'red' for x in ic_df['ic']], alpha=0.7)
ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax.axhline(y=ic_df['ic'].mean(), color='blue', linestyle='--', label=f'Mean IC={ic_df["ic"].mean():.4f}')
ax.set_title('Monthly IC (Sentiment Score vs Next-Day Return)')
ax.set_xlabel('Date')
ax.set_ylabel('Spearman IC')
ax.legend()
plt.tight_layout()
plt.savefig('fig_08_monthly_ic.png', dpi=150, bbox_inches='tight')
plt.show()
```

### 2. ICIR 计算
```python
mean_ic = ic_df['ic'].mean()
std_ic = ic_df['ic'].std()
icir = mean_ic / std_ic

print("=" * 50)
print("Signal Quality Metrics")
print("=" * 50)
print(f"Mean IC:     {mean_ic:.4f}")
print(f"IC Std:      {std_ic:.4f}")
print(f"ICIR:        {icir:.4f}")
print(f"IC > 0 pct:  {(ic_df['ic'] > 0).mean():.1%}")
print(f"Num months:  {len(ic_df)}")
```

### 3. 统计显著性检验
```python
# 全样本 t-test：IC 序列是否显著异于 0
from scipy.stats import ttest_1samp
t_stat, p_val = ttest_1samp(ic_df['ic'].dropna(), 0)
print(f"\nIC t-test: t={t_stat:.3f}, p={p_val:.4f}")
print(f"Statistically significant (p<0.05): {p_val < 0.05}")
```

### 4. Signal Decay Test
检验情绪信号的时效性：`sentiment_t` 分别对 `return_t+1`、`return_t+2`、`return_t+3` 的预测力

```python
decay_results = []
for lag in [1, 2, 3]:
    # 情绪信号预测 lag 期后的收益
    future_return = df['return_open'].shift(-lag)
    clean = pd.DataFrame({'signal': df['sentiment_score'], 'future_return': future_return}).dropna()
    ic, p = stats.spearmanr(clean['signal'], clean['future_return'])
    decay_results.append({'horizon': f't+{lag}', 'ic': ic, 'p_value': p})

decay_df = pd.DataFrame(decay_results)
print("\nSignal Decay Analysis:")
print(decay_df.to_string(index=False))

# Signal Decay 曲线
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(decay_df['horizon'], decay_df['ic'], color=['#2196F3','#64B5F6','#BBDEFB'])
ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax.set_title('Signal Decay: IC at Different Horizons')
ax.set_xlabel('Forecast Horizon')
ax.set_ylabel('Spearman IC')
for i, row in decay_df.iterrows():
    ax.text(i, row['ic'] + 0.001, f'{row["ic"]:.4f}', ha='center', fontsize=10)
plt.tight_layout()
plt.savefig('fig_09_signal_decay.png', dpi=150, bbox_inches='tight')
plt.show()
```

## 代码规范
- ICIR 结果用醒目的打印格式输出（`=` 分隔线）
- 图表保存 PNG 备用
- 月度 IC 数据保存为 DataFrame 供后续使用

## 验收标准
- [ ] 月度 IC 时序图生成（约 37 个月的柱状图）
- [ ] ICIR 数值正确计算并打印
- [ ] Signal Decay 曲线展示 3 个预测期的 IC
- [ ] t-test 结果打印，含显著性判断

<!-- FACTORY:DONE -->
