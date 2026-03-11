from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from task_006_strategy_design import SIGNAL_COLUMNS, generate_all_signals


INPUT_FILE = "hsi_features.csv"
FEE_RATE = 0.001
ANNUAL_FACTOR = 252
REQUIRED_COLUMNS = {"Date", "return_open", "return_close"}
FIG_CUM_RETURNS = "fig_10_cum_returns.png"
FIG_DRAWDOWN = "fig_11_drawdown.png"
FIG_MONTHLY_HEATMAP = "fig_12_monthly_heatmap.png"
FIG_RETURN_DIST = "fig_13_return_dist.png"


def load_data(file_path: str) -> pd.DataFrame:
    """Load feature data and enforce chronological order."""
    print(f"Loading feature data from {file_path}...")
    df = pd.read_csv(file_path)
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date").reset_index(drop=True)
    print("Feature data loaded.")
    return df


def validate_columns(df: pd.DataFrame) -> None:
    """Validate that all base columns required for backtesting exist."""
    missing_columns = REQUIRED_COLUMNS.difference(df.columns)
    if missing_columns:
        missing_str = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing_str}")


def ensure_signals(df: pd.DataFrame) -> pd.DataFrame:
    """Generate strategy signals if they are not already present."""
    if set(SIGNAL_COLUMNS).issubset(df.columns):
        return df.copy()
    return generate_all_signals(df)


def configure_plot_style() -> None:
    """Apply a consistent plotting style across all charts."""
    sns.set_style("whitegrid")
    plt.rcParams["figure.figsize"] = (12, 6)
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.labelsize"] = 11
    plt.rcParams["legend.fontsize"] = 10


def save_and_close(fig: plt.Figure, output_path: str) -> None:
    """Save figure to disk and release matplotlib memory."""
    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {output_path}")


def run_backtest(df: pd.DataFrame, signals: pd.Series, fee_rate: float = 0.0) -> pd.DataFrame:
    """
    矢量化回测引擎

    Parameters
    ----------
    df : DataFrame
        Must include Date and return_open columns.
    signals : Series
        Values in {1, -1, 0}.
    fee_rate : float
        Single-side fee rate.

    Returns
    -------
    DataFrame
        Portfolio path with daily return, cumulative return, fee, and drawdown.
    """
    portfolio = df[["Date", "return_open"]].copy()
    portfolio["signal"] = pd.Series(signals, index=df.index).fillna(0).astype("int64")
    portfolio["strategy_return"] = portfolio["signal"] * portfolio["return_open"].fillna(0.0)

    if fee_rate > 0:
        position_change = portfolio["signal"].diff().abs().fillna(0)
        portfolio["fee"] = position_change * fee_rate
        portfolio["strategy_return"] = portfolio["strategy_return"] - portfolio["fee"]
    else:
        portfolio["fee"] = 0.0

    portfolio["daily_return"] = portfolio["strategy_return"]

    cum_value = (1 + portfolio["strategy_return"]).cumprod()
    portfolio["cum_return"] = cum_value - 1
    rolling_max = cum_value.cummax()
    portfolio["drawdown"] = (cum_value - rolling_max) / rolling_max

    return portfolio


def calculate_metrics(portfolio: pd.DataFrame, annual_factor: int = ANNUAL_FACTOR) -> dict[str, str | int]:
    """Calculate a full set of formatted performance metrics."""
    returns = portfolio["strategy_return"].dropna()
    if returns.empty:
        return {
            "Total Return": "0.00%",
            "Annual Return": "0.00%",
            "Annual Volatility": "0.00%",
            "Sharpe Ratio": "0.000",
            "Max Drawdown": "0.00%",
            "Win Rate": "0.00%",
            "Total Fee Cost": "0.0000",
            "Num Trades": 0,
        }

    total_return = (1 + returns).prod() - 1
    n_years = len(returns) / annual_factor
    annual_return = (1 + total_return) ** (1 / n_years) - 1 if n_years > 0 else 0.0
    annual_vol = returns.std() * np.sqrt(annual_factor)
    sharpe = annual_return / annual_vol if annual_vol > 0 else 0.0
    max_drawdown = portfolio["drawdown"].min()

    active_days = (returns != 0).sum()
    win_rate = (returns > 0).sum() / active_days if active_days > 0 else 0.0
    total_fee = float(portfolio["fee"].sum())
    num_trades = int(portfolio["signal"].diff().abs().fillna(0).sum())

    return {
        "Total Return": f"{total_return:.2%}",
        "Annual Return": f"{annual_return:.2%}",
        "Annual Volatility": f"{annual_vol:.2%}",
        "Sharpe Ratio": f"{sharpe:.3f}",
        "Max Drawdown": f"{max_drawdown:.2%}",
        "Win Rate": f"{win_rate:.2%}",
        "Total Fee Cost": f"{total_fee:.4f}",
        "Num Trades": num_trades,
    }


def benchmark_buyhold(df: pd.DataFrame) -> pd.DataFrame:
    """买入持有基准：close-to-close return."""
    bm = df[["Date", "return_close"]].copy()
    bm["return_close"] = bm["return_close"].fillna(0.0)
    bm["cum_return"] = (1 + bm["return_close"]).cumprod() - 1
    cum_value = 1 + bm["cum_return"]
    bm["drawdown"] = (cum_value - cum_value.cummax()) / cum_value.cummax()
    return bm


def print_metrics_table(results: dict[str, dict[str, object]]) -> pd.DataFrame:
    """Print a comparison table for all strategy backtests."""
    metrics_table = pd.DataFrame(
        {name: result["metrics"] for name, result in results.items()}
    ).T
    print("\n" + "=" * 90)
    print("BACKTEST PERFORMANCE COMPARISON")
    print("=" * 90)
    print(metrics_table.to_string())
    return metrics_table


def run_all_backtests(df: pd.DataFrame) -> dict[str, dict[str, object]]:
    """Run all strategies with and without transaction fees."""
    strategies = {
        "Strategy_A": df["signal_a"],
        "Strategy_B": df["signal_b"],
        "Strategy_C": df["signal_c"],
    }

    results: dict[str, dict[str, object]] = {}
    for name, signals in strategies.items():
        for fee in (0.0, FEE_RATE):
            key = f"{name}_{'w_fee' if fee > 0 else 'no_fee'}"
            portfolio = run_backtest(df, signals, fee_rate=fee)
            metrics = calculate_metrics(portfolio)
            results[key] = {"portfolio": portfolio, "metrics": metrics}

    print_metrics_table(results)
    return results


def plot_cumulative_returns(df: pd.DataFrame, results: dict[str, dict[str, object]]) -> None:
    """Plot cumulative return curves for all strategies and the benchmark."""
    benchmark = benchmark_buyhold(df)
    fig, ax = plt.subplots(figsize=(14, 7))

    color_map = {
        "Strategy_A": "#1f77b4",
        "Strategy_B": "#ff7f0e",
        "Strategy_C": "#2ca02c",
    }

    ax.plot(
        benchmark["Date"],
        benchmark["cum_return"],
        color="black",
        linewidth=2,
        label="Benchmark Buy & Hold",
    )

    for strategy_name, color in color_map.items():
        no_fee = results[f"{strategy_name}_no_fee"]["portfolio"]
        with_fee = results[f"{strategy_name}_w_fee"]["portfolio"]
        ax.plot(no_fee["Date"], no_fee["cum_return"], color=color, linewidth=2, label=f"{strategy_name} no fee")
        ax.plot(
            with_fee["Date"],
            with_fee["cum_return"],
            color=color,
            linewidth=1.8,
            linestyle="--",
            label=f"{strategy_name} w/ fee",
        )

    ax.set_title("Cumulative Returns: All Strategies vs Benchmark")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative Return")
    ax.legend(ncol=2)
    save_and_close(fig, FIG_CUM_RETURNS)


def plot_drawdown(results: dict[str, dict[str, object]]) -> None:
    """Plot drawdown curves for all strategy variants."""
    fig, ax = plt.subplots(figsize=(14, 5))

    for name, result in results.items():
        portfolio = result["portfolio"]
        linestyle = "--" if name.endswith("w_fee") else "-"
        ax.plot(portfolio["Date"], portfolio["drawdown"], linewidth=1.5, linestyle=linestyle, label=name)

    ax.set_title("Strategy Drawdown Analysis")
    ax.set_xlabel("Date")
    ax.set_ylabel("Drawdown")
    ax.legend(ncol=2)
    save_and_close(fig, FIG_DRAWDOWN)


def plot_monthly_heatmap(portfolio: pd.DataFrame, title: str = "Monthly Returns Heatmap (Strategy A)") -> None:
    """Plot a monthly return heatmap for a single strategy portfolio."""
    monthly = portfolio[["Date", "strategy_return"]].copy()
    monthly["Date"] = pd.to_datetime(monthly["Date"])
    monthly = monthly.set_index("Date")
    monthly_ret = monthly["strategy_return"].resample("ME").sum().to_frame()
    monthly_ret["Year"] = monthly_ret.index.year
    monthly_ret["Month"] = monthly_ret.index.month
    pivot = monthly_ret.pivot(index="Year", columns="Month", values="strategy_return")
    pivot = pivot.reindex(columns=range(1, 13))

    fig, ax = plt.subplots(figsize=(14, 5))
    sns.heatmap(pivot, annot=True, fmt=".2%", cmap="RdYlGn", center=0, ax=ax)
    ax.set_title(title)
    ax.set_xlabel("Month")
    ax.set_ylabel("Year")
    save_and_close(fig, FIG_MONTHLY_HEATMAP)


def plot_return_distributions(results: dict[str, dict[str, object]]) -> None:
    """Plot return histograms for the three no-fee strategy variants."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    strategies = ["Strategy_A", "Strategy_B", "Strategy_C"]

    for i, strategy_name in enumerate(strategies):
        portfolio = results[f"{strategy_name}_no_fee"]["portfolio"]
        axes[i].hist(
            portfolio["strategy_return"].dropna(),
            bins=50,
            color="steelblue",
            alpha=0.75,
            edgecolor="white",
        )
        axes[i].axvline(0, color="red", linestyle="--", linewidth=1)
        axes[i].set_title(f"{strategy_name} Return Distribution")
        axes[i].set_xlabel("Daily Return")
        axes[i].set_ylabel("Frequency")

    save_and_close(fig, FIG_RETURN_DIST)


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

    results = run_all_backtests(df)
    plot_cumulative_returns(df, results)
    plot_drawdown(results)
    plot_monthly_heatmap(results["Strategy_A_no_fee"]["portfolio"])
    plot_return_distributions(results)


if __name__ == "__main__":
    main()
