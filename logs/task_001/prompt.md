# Task 001 — 数据加载与清洗

## 目标
实现 HSI 数据的加载、清洗和基础统计分析，为后续所有分析提供干净的数据基础。

## 工作目录
`code/`

## 输出文件
- `task_001_data_loading.py` — 数据加载与清洗模块

## 详细要求

### 1. 数据加载
```python
import pandas as pd
import numpy as np

# 加载 HSI.xlsx
df = pd.read_excel('HSI.xlsx')

# 解析日期列，按时间排序
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values('Date').reset_index(drop=True)
```

### 2. 数据检测
检测并打印以下信息：
- 数据形状（行数、列数）
- 各列数据类型
- 缺失值数量（每列）
- 重复行数量
- `Up votes + Down votes != 1` 的异常行数量（允许 1e-6 误差）

```python
# 检测情绪数据异常
df['vote_sum'] = df['Up votes'] + df['Down votes']
df['vote_anomaly'] = (df['vote_sum'] - 1).abs() > 1e-6
anomaly_count = df['vote_anomaly'].sum()
print(f"Vote sum anomaly rows: {anomaly_count}")
```

### 3. 数据清洗
- 对 `Up votes` 和 `Down votes` 使用 forward fill（`ffill`）填充缺失值
- **不使用 backward fill**（避免未来信息泄漏）
- 保留 `vote_anomaly` 标注列，不删除异常行

```python
df['Up votes'] = df['Up votes'].fillna(method='ffill')
df['Down votes'] = df['Down votes'].fillna(method='ffill')
```

### 4. 基础统计摘要
输出所有数值列的：均值、标准差、最小值、25%/50%/75% 分位数、最大值

```python
summary = df[['Open', 'High', 'Low', 'Close', 'Up votes', 'Down votes']].describe()
print(summary)
```

### 5. 保存清洗后数据
```python
df.to_csv('hsi_clean.csv', index=False)
print("Clean data saved to hsi_clean.csv")
print(f"Final shape: {df.shape}")
```

## 代码规范
- 使用 Python 函数封装各步骤
- 每个关键步骤添加 print 输出，便于 Notebook 展示
- 文件末尾添加 `if __name__ == '__main__': main()` 入口

## 验收标准
- [ ] 正确加载 HSI.xlsx，747 行左右
- [ ] 正确检测 195 条情绪缺失记录
- [ ] forward fill 正确执行，无剩余 NaN（在情绪列）
- [ ] 异常行被标注（不删除）
- [ ] 统计摘要输出完整

<!-- FACTORY:DONE -->
