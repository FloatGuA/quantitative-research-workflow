from pathlib import Path

import pandas as pd


INPUT_FILE = "hsi_features.csv"
SIGNAL_COLUMNS = ["signal_a", "signal_b", "signal_c"]


def load_data(file_path: str) -> pd.DataFrame:
    """Load feature data generated in Task 002."""
    print(f"Loading feature data from {file_path}...")
    df = pd.read_csv(file_path)
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date").reset_index(drop=True)
    print("Feature data loaded.")
    return df


def validate_columns(df: pd.DataFrame) -> None:
    """Validate that all strategy inputs are available."""
    required_columns = {
        "sentiment_score",
        "vote_imbalance",
        "extreme_bull",
        "extreme_bear",
    }
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        missing_str = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing_str}")


def _print_signal_distribution(name: str, signals: pd.Series, extra_label: str = "") -> None:
    """Print a compact distribution summary for a strategy signal series."""
    header = f"{name} Signal Distribution"
    if extra_label:
        header = f"{header} ({extra_label})"

    print(header + ":")
    print(f"  Long  (1): {(signals == 1).sum()} days ({(signals == 1).mean():.1%})")
    print(f"  Short (-1): {(signals == -1).sum()} days ({(signals == -1).mean():.1%})")
    print(f"  Hold  (0): {(signals == 0).sum()} days ({(signals == 0).mean():.1%})")


def strategy_a_signals(df: pd.DataFrame) -> pd.Series:
    """
    Long-short contrarian tail strategy.

    Economic intuition:
    Mean IC is negative, so sentiment behaves as a contrarian indicator rather
    than a trend-following one. Extreme bullish sentiment is interpreted as an
    overheated or overbought state and is shorted; extreme bearish sentiment is
    interpreted as an oversold state and is bought. The middle 60% remains flat
    to isolate whether the reversal effect is concentrated in the tails.

    Timing note:
    Signals are generated from information known on day t. The backtest engine
    should shift the signal by one period when mapping it to t+1 returns.

    Returns:
        Series with values 1 (long), -1 (short), 0 (hold).
    """
    signals = pd.Series(0, index=df.index, dtype="int64")
    signals.loc[df["extreme_bull"]] = -1
    signals.loc[df["extreme_bear"]] = 1

    _print_signal_distribution("Strategy A", signals)
    return signals


def strategy_b_signals(df: pd.DataFrame, threshold: float = 0.1) -> pd.Series:
    """
    Threshold-based contrarian strategy.

    Economic intuition:
    Mean IC is negative, so raw sentiment should be inverted before trading.
    Clearly positive sentiment is treated as a contrarian short because crowd
    optimism likely reflects overextension; clearly negative sentiment is
    treated as a contrarian long because crowd pessimism may mark oversold
    conditions. The neutral band around zero avoids weak or noisy states.

    Timing note:
    Signals use only contemporaneous sentiment information. Align with future
    returns in the backtest via a one-period shift.

    Args:
        threshold: Absolute sentiment cutoff used to enter long/short trades.

    Returns:
        Series with values 1 (long), -1 (short), 0 (hold).
    """
    signals = pd.Series(0, index=df.index, dtype="int64")
    signals.loc[df["sentiment_score"] > threshold] = -1
    signals.loc[df["sentiment_score"] < -threshold] = 1

    _print_signal_distribution("Strategy B", signals, extra_label=f"threshold={threshold}")
    return signals


def strategy_c_signals(df: pd.DataFrame, threshold: float = 0.1) -> pd.Series:
    """
    Contrarian threshold strategy with conviction filter.

    Economic intuition:
    Start from the contrarian threshold rule in Strategy B, then execute only
    when vote_imbalance is at or above its train-sample median. This keeps the
    IC-consistent contrarian direction while filtering for high-conviction
    sentiment states that may produce cleaner reversal opportunities.

    Timing note:
    The filter and base signal are both formed using information observed on
    day t. Backtests should shift the final signal by one period before trading.

    Args:
        threshold: Absolute sentiment cutoff inherited from Strategy B.

    Returns:
        Series with values 1 (long), -1 (short), 0 (hold).
    """
    if "is_train" in df.columns:
        median_imbalance = df.loc[df["is_train"], "vote_imbalance"].median()
    else:
        median_imbalance = df["vote_imbalance"].median()
    high_conviction = df["vote_imbalance"] >= median_imbalance

    base_signals = strategy_b_signals(df, threshold)
    signals = base_signals.where(high_conviction, other=0).astype("int64")

    print(
        f"\nStrategy C filter diagnostics: median_vote_imbalance={median_imbalance:.4f}, "
        f"retained_non_zero_signals={(signals != 0).sum()}/{(base_signals != 0).sum()}"
    )
    _print_signal_distribution(
        "Strategy C",
        signals,
        extra_label=f"vote filter: imbalance>={median_imbalance:.4f}",
    )
    return signals


def generate_all_signals(df: pd.DataFrame, threshold: float = 0.1) -> pd.DataFrame:
    """Generate all strategy signals and return a DataFrame copy with signal columns."""
    print("=" * 50)
    print("STRATEGY SIGNAL GENERATION")
    print("=" * 50)

    validate_columns(df)
    output = df.copy()
    output["signal_a"] = strategy_a_signals(output)
    print()
    output["signal_b"] = strategy_b_signals(output, threshold=threshold)
    print()
    output["signal_c"] = strategy_c_signals(output, threshold=threshold)

    effective_b = (output["signal_b"] != 0).sum()
    effective_c = (output["signal_c"] != 0).sum()
    reduction_ratio = float("nan") if effective_b == 0 else 1 - effective_c / effective_b

    print("\nStrategy Signal Correlation:")
    print(output[SIGNAL_COLUMNS].corr())
    print(
        "\nSignal Coverage Diagnostics:\n"
        f"  Strategy A non-zero signals: {(output['signal_a'] != 0).sum()}\n"
        f"  Strategy B non-zero signals: {effective_b}\n"
        f"  Strategy C non-zero signals: {effective_c}\n"
        f"  Strategy C reduction vs B: {reduction_ratio:.1%}"
        if pd.notna(reduction_ratio)
        else "\nSignal Coverage Diagnostics:\n  Strategy B has no active signals."
    )

    return output


def main() -> None:
    input_path = Path(INPUT_FILE)
    if not input_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_path.resolve()}. "
            "Run task_002_feature_engineering.py first to generate hsi_features.csv."
        )

    df = load_data(str(input_path))
    signal_df = generate_all_signals(df)

    print("\nSignal preview:")
    preview_columns = [col for col in ["Date", "sentiment_score", *SIGNAL_COLUMNS] if col in signal_df.columns]
    print(signal_df[preview_columns].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
