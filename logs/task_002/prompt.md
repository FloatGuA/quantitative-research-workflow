# Task 002 — 收益率构建与情绪特征工程

## 目标
基于清洗后的 HSI 数据，构建所有分析所需的收益率序列和情绪特征，并为每个特征提供经济含义说明。

## 工作目录
`code/`

## 依赖
- `hsi_clean.csv`（Task 001 输出）

## 输出文件
- `task_002_feature_engineering.py` — 特征工程模块

## 详细要求

### 1. 收益率构建

**主要收益率 — next-day open return（主信号对齐目标）**
```python
# return_t = (open_{t+1} - open_t) / open_t
df['return_open'] = df['Open'].shift(-1) / df['Open'] - 1
```

说明：使用隔日开盘价收益率，模拟"收盘前获得情绪信号，次日开盘建仓"的交易场景，避免收盘价反转偏差。

**辅助收益率 — close-to-close return（用于对比）**
```python
df['return_close'] = df['Close'].pct_change()
```

### 2. 情绪特征构建

每个特征必须附带注释说明经济含义：

```python
# sentiment_score: 情绪净值，正值表示多头情绪占优，负值表示空头情绪
df['sentiment_score'] = df['Up votes'] - df['Down votes']

# vote_imbalance: 情绪强度，绝对值越大表示投票者共识越强
df['vote_imbalance'] = (df['Up votes'] - df['Down votes']).abs()

# extreme_bull: top 20% 情绪分位数，表示极度乐观市场状态
q80 = df['sentiment_score'].quantile(0.8)
df['extreme_bull'] = df['sentiment_score'] >= q80

# extreme_bear: bottom 20% 情绪分位数，表示极度悲观市场状态
q20 = df['sentiment_score'].quantile(0.2)
df['extreme_bear'] = df['sentiment_score'] <= q20

# 滞后信号：用于 Signal Decay 分析（t-n 的情绪预测 t+1 收益）
df['sentiment_lag1'] = df['sentiment_score'].shift(1)
df['sentiment_lag2'] = df['sentiment_score'].shift(2)
df['sentiment_lag3'] = df['sentiment_score'].shift(3)
```

### 3. 情绪分位数标记
```python
# 将 sentiment_score 分为 5 个等分分位数（用于 EDA 分析）
df['sentiment_quantile'] = pd.qcut(df['sentiment_score'], q=5, labels=['Q1','Q2','Q3','Q4','Q5'])
```

### 4. 保存特征数据
```python
df.to_csv('hsi_features.csv', index=False)
print("Feature data saved to hsi_features.csv")

# 打印特征统计
feature_cols = ['sentiment_score', 'vote_imbalance', 'return_open', 'return_close']
print(df[feature_cols].describe())
print(f"\nExtreme bull days: {df['extreme_bull'].sum()}")
print(f"Extreme bear days: {df['extreme_bear'].sum()}")
```

## 代码规范
- 所有特征计算使用 pandas 矢量化操作（不用 for loop）
- 每个特征用注释说明经济含义
- 打印关键统计数据以便 Notebook 展示

## 验收标准
- [ ] return_open 使用 shift(-1)，无未来信息泄漏
- [ ] 7 个情绪特征全部计算完成
- [ ] extreme_bull/bear 各约 20% 的行被标记
- [ ] sentiment_quantile 五分组分布均匀
- [ ] hsi_features.csv 成功保存

<!-- FACTORY:DONE -->
