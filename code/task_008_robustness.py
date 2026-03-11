from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import mstats

from task_007_backtest import (
    FEE_RATE,
    INPUT_FILE,
    calculate_metrics,
    configure_plot_style,
    ensure_signals,
    load_data,
    run_backtest,
    save_and_close,
    validate_columns,
)


FIG_SENSITIVITY = "fig_14_sensitivity.png"
FIG_ROLLING_SHARPE = "fig_15_rolling_sharpe.png"
SENSITIVITY_THRESHOLDS = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
ROBUSTNESS_THRESHOLD = 0.1
ROLLING_WINDOW = 252


def parse_percent(value: str) -> float:
    """Convert a formatted percent string like '12.34%' to decimal."""
    return float(value.strip("%")) / 100


def parse_float(value: str) -> float:
    """Convert a formatted numeric string to float."""
    return float(value)


def threshold_sensitivity_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Run Strategy B threshold sensitivity analysis and save the chart."""
    sensitivity_results: list[dict[str, float]] = []

    for threshold in SENSITIVITY_THRESHOLDS:
        signals = (df["sentiment_score"] > threshold).astype(int) - (
            df["sentiment_score"] < -threshold
        ).astype(int)
        portfolio = run_backtest(df, signals, fee_rate=FEE_RATE)
        metrics = calculate_metrics(portfolio)
        sensitivity_results.append(
            {
                "threshold": threshold,
                "sharpe": parse_float(str(metrics["Sharpe Ratio"])),
                "annual_return": parse_percent(str(metrics["Annual Return"])),
                "max_drawdown": parse_percent(str(metrics["Max Drawdown"])),
            }
        )

    sensitivity_df = pd.DataFrame(sensitivity_results)
    print("Threshold Sensitivity Analysis:")
    print(sensitivity_df.to_string(index=False))

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    axes[0].plot(sensitivity_df["threshold"], sensitivity_df["sharpe"], "bo-")
    axes[0].set_title("Sharpe vs Threshold")
    axes[0].set_xlabel("Threshold")
    axes[0].set_ylabel("Sharpe Ratio")

    axes[1].plot(sensitivity_df["threshold"], sensitivity_df["annual_return"], "go-")
    axes[1].set_title("Annual Return vs Threshold")
    axes[1].set_xlabel("Threshold")
    axes[1].set_ylabel("Annual Return")

    axes[2].plot(sensitivity_df["threshold"], sensitivity_df["max_drawdown"], "ro-")
    axes[2].set_title("Max Drawdown vs Threshold")
    axes[2].set_xlabel("Threshold")
    axes[2].set_ylabel("Max Drawdown")

    save_and_close(fig, FIG_SENSITIVITY)
    return sensitivity_df


def lag_signal_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Compare performance using current and lagged sentiment signals."""
    lag_results: list[dict[str, str | int]] = []

    for lag in [0, 1, 2, 3]:
        score = df["sentiment_score"] if lag == 0 else df[f"sentiment_lag{lag}"]
        signals = (score > ROBUSTNESS_THRESHOLD).astype(int) - (
            score < -ROBUSTNESS_THRESHOLD
        ).astype(int)
        portfolio = run_backtest(df, signals, fee_rate=FEE_RATE)
        metrics = calculate_metrics(portfolio)
        lag_results.append({"lag": lag, **metrics})

    lag_df = pd.DataFrame(lag_results)
    print("\nLag Signal Analysis:")
    print(
        lag_df[["lag", "Sharpe Ratio", "Annual Return", "Max Drawdown"]].to_string(
            index=False
        )
    )
    return lag_df


def outlier_removal_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Winsorize extreme sentiment values and compare performance."""
    winsorized_df = df.copy()
    winsorized_df["sentiment_winsorized"] = mstats.winsorize(
        df["sentiment_score"].fillna(0),
        limits=[0.01, 0.01],
    )

    original_signals = (df["sentiment_score"] > ROBUSTNESS_THRESHOLD).astype(int) - (
        df["sentiment_score"] < -ROBUSTNESS_THRESHOLD
    ).astype(int)
    winsorized_signals = (
        winsorized_df["sentiment_winsorized"] > ROBUSTNESS_THRESHOLD
    ).astype(int) - (
        winsorized_df["sentiment_winsorized"] < -ROBUSTNESS_THRESHOLD
    ).astype(int)

    original_portfolio = run_backtest(df, original_signals, fee_rate=FEE_RATE)
    winsorized_portfolio = run_backtest(df, winsorized_signals, fee_rate=FEE_RATE)

    metrics_original = calculate_metrics(original_portfolio)
    metrics_winsorized = calculate_metrics(winsorized_portfolio)

    comparison_df = pd.DataFrame(
        {
            "Metric": ["Sharpe Ratio", "Annual Return", "Max Drawdown"],
            "Original": [
                metrics_original["Sharpe Ratio"],
                metrics_original["Annual Return"],
                metrics_original["Max Drawdown"],
            ],
            "Winsorized": [
                metrics_winsorized["Sharpe Ratio"],
                metrics_winsorized["Annual Return"],
                metrics_winsorized["Max Drawdown"],
            ],
        }
    )

    print("\nOutlier Removal Analysis (Strategy B, with fee):")
    print(comparison_df.to_string(index=False))
    return comparison_df


def rolling_sharpe(
    portfolio: pd.DataFrame,
    window: int = ROLLING_WINDOW,
    annual_factor: int = 252,
) -> pd.Series:
    """Calculate rolling Sharpe ratio from strategy daily returns."""
    returns = portfolio["strategy_return"]
    rolling_mean = returns.rolling(window).mean()
    rolling_std = returns.rolling(window).std()
    return (rolling_mean / rolling_std) * np.sqrt(annual_factor)


def build_strategy_results(df: pd.DataFrame) -> dict[str, dict[str, pd.DataFrame | dict[str, str | int]]]:
    """Build no-fee backtest results for Strategy A/B/C for rolling diagnostics."""
    strategies = {
        "Strategy_A": df["signal_a"],
        "Strategy_B": df["signal_b"],
        "Strategy_C": df["signal_c"],
    }

    results: dict[str, dict[str, pd.DataFrame | dict[str, str | int]]] = {}
    for name, signals in strategies.items():
        portfolio = run_backtest(df, signals, fee_rate=0.0)
        results[f"{name}_no_fee"] = {
            "portfolio": portfolio,
            "metrics": calculate_metrics(portfolio),
        }
    return results


def plot_rolling_sharpe(results: dict[str, dict[str, pd.DataFrame | dict[str, str | int]]]) -> None:
    """Plot 12-month rolling Sharpe ratios for all three strategies."""
    fig, ax = plt.subplots(figsize=(14, 5))
    for name in ["Strategy_A", "Strategy_B", "Strategy_C"]:
        portfolio = results[f"{name}_no_fee"]["portfolio"]
        rolling_values = rolling_sharpe(portfolio)
        ax.plot(portfolio["Date"], rolling_values, label=name, alpha=0.8)

    ax.axhline(0, color="black", linestyle="--", alpha=0.5)
    ax.set_title("Rolling 12-Month Sharpe Ratio")
    ax.set_xlabel("Date")
    ax.set_ylabel("Sharpe Ratio")
    ax.legend()
    save_and_close(fig, FIG_ROLLING_SHARPE)


def print_overfitting_discussion() -> None:
    """Print the overfitting risk discussion in Markdown format."""
    overfitting_discussion = """
## Overfitting Risk Discussion

1. **In-sample only**: All analysis is performed on the full dataset without out-of-sample validation.
   The results may be optimistic due to data snooping.

2. **Threshold selection**: The +/-0.1 threshold for Strategy B was chosen based on visual inspection.
   Sensitivity analysis shows whether results remain stable across nearby threshold settings.

3. **Limited history**: The sample covers only a few years of trading days.
   The strategy has not been tested across a full market cycle.

4. **Survivorship bias**: HSI is a market-cap weighted index; constituent changes are not modeled.

5. **Recommendation**: Forward-test the strategy on unseen future data before live deployment.
"""
    print("\n" + overfitting_discussion.strip())


def main() -> None:
    input_path = Path(INPUT_FILE)
    if not input_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_path.resolve()}. "
            "Run task_002_feature_engineering.py first to generate hsi_features.csv."
        )

    configure_plot_style()
    df = load_data(str(input_path))
    validate_columns(df)
    df = ensure_signals(df)

    threshold_sensitivity_analysis(df)
    lag_signal_analysis(df)
    outlier_removal_analysis(df)

    results = build_strategy_results(df)
    plot_rolling_sharpe(results)
    print_overfitting_discussion()


if __name__ == "__main__":
    main()
