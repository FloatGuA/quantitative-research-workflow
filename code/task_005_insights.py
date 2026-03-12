from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from task_004_signal_analysis import (
    INPUT_FILE,
    compute_monthly_ic,
    compute_signal_decay,
    load_data,
    run_ic_ttest,
    validate_columns,
)


HIGH_IMBALANCE_QUANTILE = 0.7
LOW_IMBALANCE_QUANTILE = 0.3


def compute_vote_imbalance_effect(df: pd.DataFrame) -> dict[str, float]:
    required_columns = {"vote_imbalance", "sentiment_score", "return_open"}
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        missing_str = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns for vote imbalance analysis: {missing_str}")

    train_df = df.loc[df["is_train"]] if "is_train" in df.columns else df

    high_cutoff = train_df["vote_imbalance"].quantile(HIGH_IMBALANCE_QUANTILE)
    low_cutoff = train_df["vote_imbalance"].quantile(LOW_IMBALANCE_QUANTILE)

    high_sample = train_df.loc[
        train_df["vote_imbalance"] >= high_cutoff,
        ["sentiment_score", "return_open"],
    ].dropna()
    low_sample = train_df.loc[
        train_df["vote_imbalance"] <= low_cutoff,
        ["sentiment_score", "return_open"],
    ].dropna()

    high_ic = np.nan
    low_ic = np.nan

    if len(high_sample) >= 2:
        high_ic, _ = stats.spearmanr(high_sample["sentiment_score"], high_sample["return_open"])
    if len(low_sample) >= 2:
        low_ic, _ = stats.spearmanr(low_sample["sentiment_score"], low_sample["return_open"])

    return {
        "high_cutoff": high_cutoff,
        "low_cutoff": low_cutoff,
        "high_ic": high_ic,
        "low_ic": low_ic,
        "high_n": len(high_sample),
        "low_n": len(low_sample),
        "ic_spread": high_ic - low_ic if not pd.isna(high_ic) and not pd.isna(low_ic) else np.nan,
    }


def _format_float(value: float) -> str:
    return f"{value:.4f}" if not pd.isna(value) else "nan"


def generate_insights(
    mean_ic: float,
    icir: float,
    decay_df: pd.DataFrame,
    ic_df: pd.DataFrame,
    ttest_p_value: float,
    vote_effect: dict[str, float],
) -> str:
    insights: list[str] = []

    if abs(mean_ic) > 0.05 and not pd.isna(icir) and abs(icir) > 0.5 and ttest_p_value < 0.05:
        if mean_ic < 0:
            pred_conclusion = (
                "情绪信号对次日收益具有统计显著的反向预测力（IC < 0，为反向指标）。"
                "统计显著仅表示关系存在，不代表原始做多正情绪方向正确；策略应反向使用。"
            )
        else:
            pred_conclusion = (
                "情绪信号对次日收益具有统计显著的预测力。"
                "统计显著表示关系存在，仍需单独确认交易方向是否与 IC 一致。"
            )
    elif abs(mean_ic) > 0.02 and ttest_p_value < 0.10:
        if mean_ic < 0:
            pred_conclusion = (
                "情绪信号对次日收益具有偏弱但可识别的反向预测力（IC < 0，为反向指标）。"
                "统计显著性不能替代方向判断，原始信号应取反。"
            )
        else:
            pred_conclusion = (
                "情绪信号对次日收益具有偏弱但可识别的预测力。"
                "统计显著性不能替代方向判断，仍需验证交易方向设置。"
            )
    else:
        pred_conclusion = "情绪信号对次日收益的预测力不显著，统计证据不足。"

    insights.append(f"**1. 统计预测力 Statistical Predictiveness**: {pred_conclusion}")
    insights.append(
        "   - "
        f"Mean IC = {_format_float(mean_ic)}, ICIR = {_format_float(icir)}, "
        f"t-test p-value = {_format_float(ttest_p_value)}"
    )

    lag_map = {row["horizon"]: row["ic"] for _, row in decay_df.iterrows()}
    lag1_ic = lag_map.get("t+1", np.nan)
    lag2_ic = lag_map.get("t+2", np.nan)
    lag3_ic = lag_map.get("t+3", np.nan)
    lag_abs = pd.Series({"t+1": abs(lag1_ic), "t+2": abs(lag2_ic), "t+3": abs(lag3_ic)}).dropna()

    all_decay_insignificant = all(
        row["p_value"] > 0.05
        for _, row in decay_df.iterrows()
        if not pd.isna(row["p_value"])
    )

    if all_decay_insignificant:
        decay_conclusion = "信号在各测试期均不显著，时效性结论不可靠。"
    elif not lag_abs.empty and lag_abs.idxmax() == "t+1" and lag_abs.loc["t+1"] > 0:
        decay_conclusion = "信号以短期为主，t+1 的预测力最强，alpha 更可能在 1 至 2 天内衰减。"
    elif not lag_abs.empty and lag_abs.idxmax() in {"t+2", "t+3"}:
        decay_conclusion = "信号并非只在次日生效，较长持有期仍保留部分预测力。"
    else:
        decay_conclusion = "信号衰减模式不明显，时效性结论仍需谨慎。"

    insights.append(f"\n**2. 信号时效性 Signal Decay**: {decay_conclusion}")
    insights.append(
        "   - "
        f"IC(t+1) = {_format_float(lag1_ic)}, "
        f"IC(t+2) = {_format_float(lag2_ic)}, "
        f"IC(t+3) = {_format_float(lag3_ic)}"
    )

    high_ic = vote_effect["high_ic"]
    low_ic = vote_effect["low_ic"]
    ic_spread = vote_effect["ic_spread"]
    if not pd.isna(high_ic) and not pd.isna(low_ic) and abs(high_ic) > abs(low_ic):
        vote_conclusion = "高 vote_imbalance 样本的 IC 更强，说明共识度高时信号质量更好，可作为过滤器。"
    elif not pd.isna(high_ic) and not pd.isna(low_ic):
        vote_conclusion = "高 vote_imbalance 并未明显提升 IC，情绪强度过滤的增益有限。"
    else:
        vote_conclusion = "vote_imbalance 分层样本不足，暂时无法确认强度过滤是否有效。"

    insights.append(f"\n**3. 投票强度 Vote Imbalance**: {vote_conclusion}")
    insights.append(
        "   - "
        f"High group IC = {_format_float(high_ic)} (n={vote_effect['high_n']}), "
        f"Low group IC = {_format_float(low_ic)} (n={vote_effect['low_n']}), "
        f"Spread = {_format_float(ic_spread)}"
    )

    positive_ic_pct = (ic_df["ic"] > 0).mean()
    if mean_ic < 0:
        negative_ic_pct = (ic_df["ic"] < 0).mean()
        stability = (
            f"信号在 {negative_ic_pct:.0%} 的月份中保持负 IC，方向上更接近稳定的反向指标；"
            f"仅有 {positive_ic_pct:.0%} 的月份为正。"
        )
    elif positive_ic_pct >= 0.6 and mean_ic > 0:
        stability = f"信号在 {positive_ic_pct:.0%} 的月份中保持正向 IC，稳定性较强。"
    elif positive_ic_pct >= 0.5:
        stability = f"信号在 {positive_ic_pct:.0%} 的月份中为正，具备一定稳定性但一致性一般。"
    else:
        stability = f"信号仅在 {positive_ic_pct:.0%} 的月份中为正，跨市场状态稳定性存疑。"

    insights.append(f"\n**4. 信号稳定性 Signal Stability**: {stability}")
    insights.append(
        "   - "
        f"Positive IC months = {positive_ic_pct:.0%}, Monthly observations = {len(ic_df)}"
    )

    return "\n".join(insights)


def generate_english_summary(
    mean_ic: float,
    icir: float,
    decay_df: pd.DataFrame,
    ic_df: pd.DataFrame,
    vote_effect: dict[str, float],
) -> str:
    lag_map = {row["horizon"]: row["ic"] for _, row in decay_df.iterrows()}
    positive_ic_pct = (ic_df["ic"] > 0).mean()

    lines = [
        "- **Predictiveness**: "
        f"Mean IC = {_format_float(mean_ic)} and ICIR = {_format_float(icir)} summarize the signal's base efficacy.",
    ]
    if mean_ic < 0:
        lines.append(
            "- **Signal Direction**: IC < 0 — this is a contrarian signal. "
            "Positive sentiment predicts negative returns. Strategies should short on high sentiment and go long on low sentiment."
        )
    lines.extend(
        [
            "- **Decay**: "
            f"IC(t+1) = {_format_float(lag_map.get('t+1', np.nan))}, "
            f"IC(t+2) = {_format_float(lag_map.get('t+2', np.nan))}, "
            f"IC(t+3) = {_format_float(lag_map.get('t+3', np.nan))}.",
            "- **Vote Imbalance Filter**: "
            f"High-consensus days show IC = {_format_float(vote_effect['high_ic'])} versus "
            f"{_format_float(vote_effect['low_ic'])} on low-consensus days.",
            "- **Stability**: "
            f"{positive_ic_pct:.0%} of monthly IC observations are positive.",
        ]
    )
    return "\n".join(lines)


def build_markdown_content(
    mean_ic: float,
    icir: float,
    decay_df: pd.DataFrame,
    ic_df: pd.DataFrame,
    ttest_p_value: float,
    vote_effect: dict[str, float],
) -> str:
    insights_text = generate_insights(
        mean_ic=mean_ic,
        icir=icir,
        decay_df=decay_df,
        ic_df=ic_df,
        ttest_p_value=ttest_p_value,
        vote_effect=vote_effect,
    )
    english_summary = generate_english_summary(
        mean_ic=mean_ic,
        icir=icir,
        decay_df=decay_df,
        ic_df=ic_df,
        vote_effect=vote_effect,
    )

    lag_map = {row["horizon"]: row["ic"] for _, row in decay_df.iterrows()}
    trading_note = (
        "- **Direction**: IC < 0 implies a contrarian mapping; high sentiment should be shorted and low sentiment should be bought.\n"
        if mean_ic < 0
        else ""
    )
    return f"""
## 6. Signal Analysis Insights

### Key Findings | 核心洞察

{insights_text}

### Interpretation for Trading | 交易含义

Based on the signal analysis:
- **Entry**: Use daily sentiment score as the primary signal.
{trading_note}- **Signal Quality**: ICIR = {_format_float(icir)}.
- **Decay**: IC(t+1) = {_format_float(lag_map.get("t+1", np.nan))}, suggesting focus on short-horizon positioning when the front-end IC is strongest.
- **Filter**: Use `vote_imbalance` as a quality filter when high-consensus days show stronger IC.

### English Summary

{english_summary}
""".strip()


def main() -> None:
    input_path = Path(INPUT_FILE)
    if not input_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_path.resolve()}. "
            "Run task_002_feature_engineering.py first to generate hsi_features.csv."
        )

    df = load_data(str(input_path))
    validate_columns(df)

    ic_df = compute_monthly_ic(df)
    decay_df = compute_signal_decay(df)
    metrics = {
        "mean_ic": ic_df["ic"].mean(),
        "std_ic": ic_df["ic"].std(),
    }
    metrics["icir"] = (
        np.nan
        if pd.isna(metrics["std_ic"]) or np.isclose(metrics["std_ic"], 0)
        else metrics["mean_ic"] / metrics["std_ic"]
    )
    _, ttest_p_value = run_ic_ttest(ic_df)
    vote_effect = compute_vote_imbalance_effect(df)

    insight_report = generate_insights(
        mean_ic=metrics["mean_ic"],
        icir=metrics["icir"],
        decay_df=decay_df,
        ic_df=ic_df,
        ttest_p_value=ttest_p_value,
        vote_effect=vote_effect,
    )

    print("=" * 60)
    print("SIGNAL ANALYSIS INSIGHTS")
    print("=" * 60)
    print(insight_report)
    print("=" * 60)

    markdown_content = build_markdown_content(
        mean_ic=metrics["mean_ic"],
        icir=metrics["icir"],
        decay_df=decay_df,
        ic_df=ic_df,
        ttest_p_value=ttest_p_value,
        vote_effect=vote_effect,
    )
    print(markdown_content)


if __name__ == "__main__":
    main()
