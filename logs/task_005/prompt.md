# Task 005 — Insight 总结

## 目标
基于 Task 4 的信号分析结果，撰写结构化的中英文洞察总结，嵌入 Notebook 作为 Markdown cell。

## 工作目录
`code/`

## 依赖
- `hsi_features.csv`（Task 002 输出）
- Task 004 的分析逻辑（需重新计算指标）

## 输出文件
- `task_005_insights.py` — Insight 生成模块（动态计算指标，生成结论文本）

## 详细要求

### 1. 动态生成 Insight 文本
基于实际计算的指标值，自动生成文字结论：

```python
def generate_insights(mean_ic, icir, decay_results, ic_df):
    """基于量化指标生成结构化 Insight 文本"""

    insights = []

    # 1. 统计预测力
    if abs(mean_ic) > 0.05 and icir > 0.5:
        pred_conclusion = "情绪信号对次日收益具有统计显著的预测力（IC显著异于0）"
    elif abs(mean_ic) > 0.02:
        pred_conclusion = "情绪信号对次日收益具有微弱但存在的预测力"
    else:
        pred_conclusion = "情绪信号对次日收益的预测力不显著"

    insights.append(f"**1. 统计预测力**: {pred_conclusion}")
    insights.append(f"   - Mean IC = {mean_ic:.4f}, ICIR = {icir:.4f}")

    # 2. 信号时效性
    lag1_ic = decay_results[0]['ic']
    lag2_ic = decay_results[1]['ic']
    lag3_ic = decay_results[2]['ic']

    if abs(lag1_ic) > abs(lag2_ic) and abs(lag1_ic) > abs(lag3_ic):
        decay_conclusion = "信号以短期为主（t+1 预测力最强），alpha 在 1-2 天内衰减"
    else:
        decay_conclusion = "信号衰减模式不明显，可能存在持续性中期影响"

    insights.append(f"\n**2. 信号时效性**: {decay_conclusion}")
    insights.append(f"   - IC(t+1)={lag1_ic:.4f}, IC(t+2)={lag2_ic:.4f}, IC(t+3)={lag3_ic:.4f}")

    # 3. 投票强度影响
    insights.append("\n**3. 投票强度**: 高 vote_imbalance 日的信号应更为可靠（见 Strategy C 验证）")
    insights.append("   - vote_imbalance 作为信号过滤器，筛选共识度高的交易日")

    # 4. 市场状态稳定性
    positive_ic_pct = (ic_df['ic'] > 0).mean()
    if positive_ic_pct > 0.6:
        stability = f"信号在 {positive_ic_pct:.0%} 的月份中保持正向 IC，具有较强稳定性"
    else:
        stability = f"信号仅在 {positive_ic_pct:.0%} 的月份中为正 IC，稳定性存疑"

    insights.append(f"\n**4. 信号稳定性**: {stability}")

    return "\n".join(insights)
```

### 2. 打印完整 Insight 报告
```python
print("=" * 60)
print("SIGNAL ANALYSIS INSIGHTS")
print("=" * 60)
print(generate_insights(mean_ic, icir, decay_results, ic_df))
print("=" * 60)
```

### 3. 生成 Notebook Markdown Cell 内容
```python
# 生成适合嵌入 Notebook 的 Markdown 格式
markdown_content = f"""
## 6. Signal Analysis Insights

### Key Findings

{generate_insights(mean_ic, icir, decay_results, ic_df)}

### Interpretation for Trading

Based on the signal analysis:
- **Entry**: Use daily sentiment score as the primary signal
- **Signal Quality**: ICIR = {icir:.4f} (>0.5 suggests usable signal)
- **Decay**: The signal is primarily short-term, suggesting intraday/next-day positioning
- **Filter**: Apply vote_imbalance filter to improve signal quality (Strategy C)
"""

print(markdown_content)
```

## 代码规范
- Insight 文本使用中文，英文指标名保持英文
- 结论应基于实际计算的数值，动态生成（不硬编码结论）
- 需要重新加载 `hsi_features.csv` 并重新计算 IC 指标

## 验收标准
- [ ] 动态生成基于实际数值的 4 个维度 Insight
- [ ] 结论表述准确反映指标数值含义
- [ ] Markdown 格式输出适合嵌入 Notebook

<!-- FACTORY:DONE -->
