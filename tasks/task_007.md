# Task 007 — 回测引擎

## 目标
实现矢量化回测引擎，对三种策略运行无手续费和有手续费两个版本，计算全套绩效指标，生成可视化报告。

## 工作目录
`code/`

## 依赖
- `hsi_features.csv`（Task 002 输出）
- Task 006 策略信号逻辑（需在本文件中重新实现或 import）

## 输出文件
- `task_007_backtest.py` — 回测引擎模块

## 详细要求

### 1. 回测引擎核心函数

```python
def run_backtest(df, signals, fee_rate=0.0):
    """
    矢量化回测引擎

    Parameters:
    -----------
    df : DataFrame，含 return_open 列（次日收益率）
    signals : Series，值为 1（long）、-1（short）、0（hold）
    fee_rate : float，单边手续费率（默认 0，含手续费版传 0.001）

    Returns:
    --------
    portfolio : DataFrame，含 daily_return、cum_return、drawdown 等列
    metrics : dict，绩效指标
    """
    portfolio = df[['Date', 'return_open']].copy()
    portfolio['signal'] = signals.values

    # 策略日收益：信号方向 × 次日收益率
    # 注意：信号在 t 日收盘后确定，t+1 日开盘建仓
    portfolio['strategy_return'] = portfolio['signal'] * portfolio['return_open']

    # 手续费：当信号发生变化（换仓）时触发单边手续费
    if fee_rate > 0:
        position_change = portfolio['signal'].diff().abs()
        # 换仓成本：仓位变化量 × 手续费（做多做空都收）
        portfolio['fee'] = position_change * fee_rate
        portfolio['strategy_return'] = portfolio['strategy_return'] - portfolio['fee']
    else:
        portfolio['fee'] = 0.0

    # 累计收益
    portfolio['cum_return'] = (1 + portfolio['strategy_return']).cumprod() - 1

    # 最大回撤
    cum_value = (1 + portfolio['strategy_return']).cumprod()
    rolling_max = cum_value.expanding().max()
    portfolio['drawdown'] = (cum_value - rolling_max) / rolling_max

    return portfolio
```

### 2. 绩效指标计算

```python
def calculate_metrics(portfolio, annual_factor=252):
    """计算完整绩效指标"""
    returns = portfolio['strategy_return'].dropna()

    # 年化收益
    total_return = (1 + returns).prod() - 1
    n_years = len(returns) / annual_factor
    annual_return = (1 + total_return) ** (1 / n_years) - 1

    # Sharpe Ratio（假设无风险利率为 0）
    annual_vol = returns.std() * np.sqrt(annual_factor)
    sharpe = annual_return / annual_vol if annual_vol > 0 else 0

    # 最大回撤
    max_drawdown = portfolio['drawdown'].min()

    # 胜率
    win_rate = (returns > 0).sum() / (returns != 0).sum() if (returns != 0).sum() > 0 else 0

    # 手续费总成本
    total_fee = portfolio['fee'].sum()

    metrics = {
        'Total Return': f"{total_return:.2%}",
        'Annual Return': f"{annual_return:.2%}",
        'Annual Volatility': f"{annual_vol:.2%}",
        'Sharpe Ratio': f"{sharpe:.3f}",
        'Max Drawdown': f"{max_drawdown:.2%}",
        'Win Rate': f"{win_rate:.2%}",
        'Total Fee Cost': f"{total_fee:.4f}",
        'Num Trades': int(portfolio['signal'].diff().abs().sum())
    }
    return metrics
```

### 3. 基准收益（买入持有）

```python
def benchmark_buyhold(df):
    """买入持有基准：close-to-close return"""
    bm = df[['Date', 'return_close']].copy()
    bm['cum_return'] = (1 + bm['return_close']).cumprod() - 1
    return bm
```

### 4. 运行所有回测并打印比较表

```python
def run_all_backtests(df):
    strategies = {
        'Strategy_A': df['signal_a'],
        'Strategy_B': df['signal_b'],
        'Strategy_C': df['signal_c'],
    }

    results = {}
    for name, signals in strategies.items():
        for fee in [0.0, 0.001]:
            key = f"{name}_{'w_fee' if fee > 0 else 'no_fee'}"
            portfolio = run_backtest(df, signals, fee_rate=fee)
            metrics = calculate_metrics(portfolio)
            results[key] = {'portfolio': portfolio, 'metrics': metrics}

    # 打印绩效对比表
    print_metrics_table(results)
    return results
```

### 5. 可视化（4 张图）

**图 10：累计收益曲线（所有策略 + 基准）**
```python
# 6条线：3策略×无手续费版 + 基准，另加有手续费版虚线
fig, ax = plt.subplots(figsize=(14, 7))
# ... 每个策略绘制实线（无费）和虚线（有费）
ax.set_title('Cumulative Returns: All Strategies vs Benchmark')
plt.savefig('fig_10_cum_returns.png', dpi=150)
plt.show()
```

**图 11：回撤曲线**
```python
fig, ax = plt.subplots(figsize=(14, 5))
# ... 各策略回撤
ax.set_title('Strategy Drawdown Analysis')
plt.savefig('fig_11_drawdown.png', dpi=150)
plt.show()
```

**图 12：月度收益热力图**
```python
# Strategy A 为例的月度收益热力图
import seaborn as sns
monthly_ret = portfolio['strategy_return'].resample('M', on='Date').sum().to_frame()
monthly_ret['Year'] = monthly_ret.index.year
monthly_ret['Month'] = monthly_ret.index.month
pivot = monthly_ret.pivot(index='Year', columns='Month', values='strategy_return')
fig, ax = plt.subplots(figsize=(14, 5))
sns.heatmap(pivot, annot=True, fmt='.2%', cmap='RdYlGn', center=0, ax=ax)
ax.set_title('Monthly Returns Heatmap (Strategy A)')
plt.savefig('fig_12_monthly_heatmap.png', dpi=150)
plt.show()
```

**图 13：收益分布直方图**
```python
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for i, (name, signals) in enumerate(strategies.items()):
    portfolio = results[f'{name}_no_fee']['portfolio']
    axes[i].hist(portfolio['strategy_return'].dropna(), bins=50, color='steelblue', alpha=0.7)
    axes[i].axvline(0, color='red', linestyle='--')
    axes[i].set_title(f'{name} Return Distribution')
plt.savefig('fig_13_return_dist.png', dpi=150)
plt.show()
```

## 代码规范
- 回测引擎纯矢量化，禁止 for loop 遍历日期
- 手续费在换仓时触发，非每日收取
- 所有绩效指标以格式化字符串输出（方便 Notebook 展示）

## 验收标准
- [ ] 3 策略 × 2 版本（含/不含手续费）= 6 组回测全部完成
- [ ] 绩效指标表包含所有 8 项指标
- [ ] 4 张可视化图全部生成
- [ ] 基准买入持有收益正确计算

<!-- FACTORY:DONE -->
