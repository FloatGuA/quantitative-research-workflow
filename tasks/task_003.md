# Task 003 — 探索性数据分析（EDA）

## 目标
生成全套 EDA 可视化，所有图表内嵌于最终 Notebook，帮助理解数据特征和情绪-收益关系。

## 工作目录
`code/`

## 依赖
- `hsi_features.csv`（Task 002 输出）

## 输出文件
- `task_003_eda.py` — EDA 可视化模块

## 详细要求

### 图表清单（必须全部实现）

#### 图 1：价格时序图
```python
# HSI Close price over time
fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(df['Date'], df['Close'], color='steelblue', linewidth=1)
ax.set_title('HSI Close Price (2022-2025)')
ax.set_xlabel('Date')
ax.set_ylabel('Price (HKD)')
plt.tight_layout()
plt.savefig('fig_01_price_series.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### 图 2：情绪叠加价格（双轴）
```python
fig, ax1 = plt.subplots(figsize=(14, 5))
ax2 = ax1.twinx()
ax1.plot(df['Date'], df['Close'], color='steelblue', alpha=0.7, label='Close')
ax2.plot(df['Date'], df['sentiment_score'], color='orange', alpha=0.7, label='Sentiment')
ax1.set_title('HSI Price vs Sentiment Score')
# 添加图例、标签
plt.tight_layout()
plt.savefig('fig_02_price_sentiment.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### 图 3：情绪分布直方图 + KDE
```python
fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(df['sentiment_score'].dropna(), bins=50, density=True, alpha=0.6, color='steelblue', label='Histogram')
df['sentiment_score'].dropna().plot.kde(ax=ax, color='orange', label='KDE')
ax.set_title('Sentiment Score Distribution')
ax.set_xlabel('Sentiment Score')
ax.legend()
plt.tight_layout()
plt.savefig('fig_03_sentiment_dist.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### 图 4：情绪 vs 未来收益散点图（含趋势线）
```python
from scipy import stats
clean = df[['sentiment_score', 'return_open']].dropna()
slope, intercept, r, p, se = stats.linregress(clean['sentiment_score'], clean['return_open'])

fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(clean['sentiment_score'], clean['return_open'], alpha=0.3, s=10)
x_line = np.linspace(clean['sentiment_score'].min(), clean['sentiment_score'].max(), 100)
ax.plot(x_line, slope * x_line + intercept, 'r-', linewidth=2)
ax.set_title(f'Sentiment vs Next-Day Return (r={r:.3f}, p={p:.3f})')
ax.set_xlabel('Sentiment Score (t)')
ax.set_ylabel('Return Open (t+1)')
plt.tight_layout()
plt.savefig('fig_04_scatter.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### 图 5：分位数平均收益柱状图（5 组）
```python
quant_returns = df.groupby('sentiment_quantile')['return_open'].mean()
fig, ax = plt.subplots(figsize=(8, 5))
colors = ['#d73027','#fc8d59','#fee090','#91bfdb','#4575b4']
quant_returns.plot(kind='bar', ax=ax, color=colors)
ax.set_title('Average Next-Day Return by Sentiment Quantile')
ax.set_xlabel('Sentiment Quantile')
ax.set_ylabel('Mean Return')
ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('fig_05_quantile_returns.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### 图 6：Cumulative Average Return by Sentiment Quantile（核心图）
```python
# 5条累积平均收益曲线
fig, ax = plt.subplots(figsize=(14, 6))
for q in ['Q1','Q2','Q3','Q4','Q5']:
    mask = df['sentiment_quantile'] == q
    cum_returns = df.loc[mask, 'return_open'].expanding().mean()
    ax.plot(df.loc[mask, 'Date'].values, cum_returns.values, label=f'Q{q[-1]}')
ax.set_title('Cumulative Average Return by Sentiment Quantile')
ax.set_xlabel('Date')
ax.set_ylabel('Cumulative Average Return')
ax.legend()
plt.tight_layout()
plt.savefig('fig_06_cumulative_quantile.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### 图 7：特征相关性热力图
```python
corr_cols = ['sentiment_score', 'vote_imbalance', 'return_open', 'return_close',
             'sentiment_lag1', 'sentiment_lag2', 'sentiment_lag3']
corr = df[corr_cols].corr(method='spearman')
fig, ax = plt.subplots(figsize=(10, 8))
import seaborn as sns
sns.heatmap(corr, annot=True, fmt='.3f', cmap='RdBu_r', center=0, ax=ax)
ax.set_title('Spearman Correlation Heatmap')
plt.tight_layout()
plt.savefig('fig_07_correlation.png', dpi=150, bbox_inches='tight')
plt.show()
```

## 代码规范
- 所有图表调用 `plt.show()` 以便 Notebook 内嵌显示
- 同时保存 PNG 文件备用
- 设置 matplotlib 字体大小：`plt.rcParams['font.size'] = 12`
- 图表标题和标签使用英文

## 验收标准
- [ ] 7 张图表全部生成且显示正常
- [ ] 图 6（Cumulative Average Return by Quantile）有 5 条颜色区分的曲线
- [ ] 图 4 趋势线可见，含 r 和 p 值标注
- [ ] 图 7 热力图显示 spearman 相关系数

<!-- FACTORY:DONE -->
