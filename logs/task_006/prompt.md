# Task 006 — 策略设计

## 目标
定义三种量化交易策略，每种含经济直觉说明和信号生成逻辑，为 Task 7 回测引擎提供输入。

## 工作目录
`code/`

## 依赖
- `hsi_features.csv`（Task 002 输出）

## 输出文件
- `task_006_strategy_design.py` — 策略定义模块

## 详细要求

### Strategy A — Long-Short Portfolio（主策略）
**经济直觉**：行业标准信号检验方法。做多情绪最好的前 20% 交易日，做空情绪最差的后 20%，检验情绪分布两端的收益差异是否显著。

```python
def strategy_a_signals(df):
    """
    Long-Short Portfolio Strategy
    Long: sentiment_score in top 20% (extreme_bull)
    Short: sentiment_score in bottom 20% (extreme_bear)
    Hold: otherwise
    Returns: Series with values 1 (long), -1 (short), 0 (hold)
    """
    signals = pd.Series(0, index=df.index)
    signals[df['extreme_bull']] = 1
    signals[df['extreme_bear']] = -1

    print("Strategy A Signal Distribution:")
    print(f"  Long  (1): {(signals==1).sum()} days ({(signals==1).mean():.1%})")
    print(f"  Short (-1): {(signals==-1).sum()} days ({(signals==-1).mean():.1%})")
    print(f"  Hold  (0): {(signals==0).sum()} days ({(signals==0).mean():.1%})")
    return signals
```

### Strategy B — Threshold Strategy
**经济直觉**：基于情绪净值阈值的趋势跟随策略。当情绪明显偏多（>0.1）时做多，明显偏空（<-0.1）时做空，情绪中性时空仓。阈值 ±0.1 可在稳健性检验中敏感性分析。

```python
def strategy_b_signals(df, threshold=0.1):
    """
    Threshold Strategy
    Long:  sentiment_score > threshold
    Short: sentiment_score < -threshold
    Hold:  otherwise (neutral zone)
    """
    signals = pd.Series(0, index=df.index)
    signals[df['sentiment_score'] > threshold] = 1
    signals[df['sentiment_score'] < -threshold] = -1

    print(f"Strategy B Signal Distribution (threshold={threshold}):")
    print(f"  Long  (1): {(signals==1).sum()} days ({(signals==1).mean():.1%})")
    print(f"  Short (-1): {(signals==-1).sum()} days ({(signals==-1).mean():.1%})")
    print(f"  Hold  (0): {(signals==0).sum()} days ({(signals==0).mean():.1%})")
    return signals
```

### Strategy C — Volume Filter Strategy
**经济直觉**：在 Strategy B 基础上加入信号质量过滤。只在 vote_imbalance（情绪强度）高于中位数时执行信号，低强度时空仓。高共识度的情绪信号噪声更低，预期能提升 Sharpe Ratio。

```python
def strategy_c_signals(df, threshold=0.1):
    """
    Volume Filter Strategy
    Execute Strategy B signals only when vote_imbalance > median
    Otherwise: hold (0)
    """
    median_imbalance = df['vote_imbalance'].median()
    high_conviction = df['vote_imbalance'] >= median_imbalance

    # Base signals from Strategy B
    base_signals = strategy_b_signals(df, threshold)

    # Apply volume filter
    signals = base_signals.where(high_conviction, other=0)

    print(f"\nStrategy C Signal Distribution (vote filter: imbalance>={median_imbalance:.4f}):")
    print(f"  Long  (1): {(signals==1).sum()} days ({(signals==1).mean():.1%})")
    print(f"  Short (-1): {(signals==-1).sum()} days ({(signals==-1).mean():.1%})")
    print(f"  Hold  (0): {(signals==0).sum()} days ({(signals==0).mean():.1%})")
    return signals
```

### 策略汇总输出
```python
def generate_all_signals(df):
    """生成所有策略信号并返回 DataFrame"""
    print("=" * 50)
    print("STRATEGY SIGNAL GENERATION")
    print("=" * 50)

    df = df.copy()
    df['signal_a'] = strategy_a_signals(df)
    print()
    df['signal_b'] = strategy_b_signals(df)
    print()
    df['signal_c'] = strategy_c_signals(df)

    # 信号相关性
    print("\nStrategy Signal Correlation:")
    print(df[['signal_a', 'signal_b', 'signal_c']].corr())

    return df
```

## 代码规范
- 每个策略函数包含完整的经济直觉 docstring
- 信号必须基于已知信息（当期情绪预测次期收益，用 shift(1) 在回测中对齐）
- 阈值参数化，方便稳健性测试修改

## 验收标准
- [ ] 三个策略函数均已实现，签名清晰
- [ ] Strategy A 约 20% long + 20% short + 60% hold
- [ ] Strategy C 比 Strategy B 的有效信号数约减少 50%
- [ ] 每个策略有经济直觉说明

<!-- FACTORY:DONE -->
