from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from scipy.stats import ttest_1samp


INPUT_FILE = "hsi_features.csv"
MONTHLY_IC_FIG = "fig_08_monthly_ic.png"
SIGNAL_DECAY_FIG = "fig_09_signal_decay.png"
MONTHLY_IC_OUTPUT = "monthly_ic.csv"
SIGNAL_DECAY_OUTPUT = "signal_decay.csv"
MIN_MONTHLY_OBSERVATIONS = 5
DECAY_HORIZONS = [1, 2, 3]
FONT_SIZE = 12


def load_data(file_path: str) -> pd.DataFrame:
    print(f"Loading feature data from {file_path}...")
    df = pd.read_csv(file_path)
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date").reset_index(drop=True)
    print("Feature data loaded.")
    return df


def validate_columns(df: pd.DataFrame) -> None:
    required_columns = {"Date", "sentiment_score", "return_open"}
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        missing_str = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing_str}")


def configure_plot_style() -> None:
    plt.rcParams["font.size"] = FONT_SIZE
    sns.set_style("whitegrid")


def save_and_show(fig: plt.Figure, output_path: str) -> None:
    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.show()
    plt.close(fig)
    print(f"Saved {output_path}")


def compute_monthly_ic(df: pd.DataFrame) -> pd.DataFrame:
    working = df.copy()
    working["year_month"] = working["Date"].dt.to_period("M")
    monthly_ic = []

    for period, group in working.groupby("year_month"):
        clean = group[["sentiment_score", "return_open"]].dropna()
        if len(clean) < MIN_MONTHLY_OBSERVATIONS:
            continue

        ic, p_value = stats.spearmanr(clean["sentiment_score"], clean["return_open"])
        monthly_ic.append(
            {
                "period": period,
                "ic": ic,
                "p_value": p_value,
                "n": len(clean),
            }
        )

    ic_df = pd.DataFrame(monthly_ic)
    if ic_df.empty:
        raise ValueError(
            "No monthly IC values were produced. Check that hsi_features.csv has enough "
            "non-null sentiment_score and return_open observations per month."
        )

    ic_df["period_dt"] = ic_df["period"].dt.to_timestamp()
    return ic_df


def plot_monthly_ic(ic_df: pd.DataFrame) -> None:
    mean_ic = ic_df["ic"].mean()
    colors = ["green" if x > 0 else "red" for x in ic_df["ic"]]

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.bar(ic_df["period_dt"], ic_df["ic"], width=20, color=colors, alpha=0.7)
    ax.axhline(y=0, color="black", linestyle="-", linewidth=0.5)
    ax.axhline(
        y=mean_ic,
        color="blue",
        linestyle="--",
        label=f"Mean IC={mean_ic:.4f}",
    )
    ax.set_title("Monthly IC (Sentiment Score vs Next-Day Return)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Spearman IC")
    ax.legend()
    save_and_show(fig, MONTHLY_IC_FIG)


def print_ic_metrics(ic_df: pd.DataFrame) -> dict[str, float]:
    mean_ic = ic_df["ic"].mean()
    std_ic = ic_df["ic"].std()
    ic_positive_pct = (ic_df["ic"] > 0).mean()
    icir = np.nan if pd.isna(std_ic) or np.isclose(std_ic, 0) else mean_ic / std_ic

    print("=" * 50)
    print("Signal Quality Metrics")
    print("=" * 50)
    print(f"Mean IC:     {mean_ic:.4f}")
    print(f"IC Std:      {std_ic:.4f}")
    print(f"ICIR:        {icir:.4f}" if not pd.isna(icir) else "ICIR:        nan")
    print(f"IC > 0 pct:  {ic_positive_pct:.1%}")
    print(f"Num months:  {len(ic_df)}")

    return {
        "mean_ic": mean_ic,
        "std_ic": std_ic,
        "icir": icir,
        "ic_positive_pct": ic_positive_pct,
    }


def run_ic_ttest(ic_df: pd.DataFrame) -> tuple[float, float]:
    ic_series = ic_df["ic"].dropna()
    if len(ic_series) < 2:
        raise ValueError("At least two monthly IC observations are required for the t-test.")

    t_stat, p_val = ttest_1samp(ic_series, 0)
    print(f"\nIC t-test: t={t_stat:.3f}, p={p_val:.4f}")
    print(f"Statistically significant (p<0.05): {p_val < 0.05}")
    return t_stat, p_val


def compute_signal_decay(df: pd.DataFrame) -> pd.DataFrame:
    decay_results = []

    for lag in DECAY_HORIZONS:
        future_return = df["return_open"].shift(-lag)
        clean = pd.DataFrame(
            {
                "signal": df["sentiment_score"],
                "future_return": future_return,
            }
        ).dropna()
        if clean.empty:
            decay_results.append({"horizon": f"t+{lag}", "ic": np.nan, "p_value": np.nan, "n": 0})
            continue

        ic, p_value = stats.spearmanr(clean["signal"], clean["future_return"])
        decay_results.append(
            {
                "horizon": f"t+{lag}",
                "ic": ic,
                "p_value": p_value,
                "n": len(clean),
            }
        )

    return pd.DataFrame(decay_results)


def print_signal_decay(decay_df: pd.DataFrame) -> None:
    print("\nSignal Decay Analysis:")
    print(decay_df.to_string(index=False))


def plot_signal_decay(decay_df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(decay_df["horizon"], decay_df["ic"], color=["#2196F3", "#64B5F6", "#BBDEFB"])
    ax.axhline(y=0, color="black", linestyle="-", linewidth=0.5)
    ax.set_title("Signal Decay: IC at Different Horizons")
    ax.set_xlabel("Forecast Horizon")
    ax.set_ylabel("Spearman IC")

    for i, row in decay_df.iterrows():
        if pd.isna(row["ic"]):
            continue
        offset = 0.001 if row["ic"] >= 0 else -0.003
        ax.text(i, row["ic"] + offset, f"{row['ic']:.4f}", ha="center", fontsize=10)

    save_and_show(fig, SIGNAL_DECAY_FIG)


def save_analysis_tables(ic_df: pd.DataFrame, decay_df: pd.DataFrame) -> None:
    ic_to_save = ic_df.copy()
    ic_to_save["period"] = ic_to_save["period"].astype(str)
    ic_to_save.to_csv(MONTHLY_IC_OUTPUT, index=False)
    decay_df.to_csv(SIGNAL_DECAY_OUTPUT, index=False)
    print(f"Saved {MONTHLY_IC_OUTPUT}")
    print(f"Saved {SIGNAL_DECAY_OUTPUT}")


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

    ic_df = compute_monthly_ic(df)
    plot_monthly_ic(ic_df)
    print_ic_metrics(ic_df)
    run_ic_ttest(ic_df)

    decay_df = compute_signal_decay(df)
    print_signal_decay(decay_df)
    plot_signal_decay(decay_df)

    save_analysis_tables(ic_df, decay_df)


if __name__ == "__main__":
    main()
