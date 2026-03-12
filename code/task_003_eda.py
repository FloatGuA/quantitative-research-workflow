from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats


INPUT_FILE = "hsi_features.csv"
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
    required_columns = {
        "Date",
        "Close",
        "sentiment_score",
        "return_open",
        "return_close",
        "vote_imbalance",
        "sentiment_lag1",
        "sentiment_lag2",
        "sentiment_lag3",
    }
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


def plot_price_series(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(df["Date"], df["Close"], color="steelblue", linewidth=1)
    ax.set_title("HSI Close Price (2022-2025)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (HKD)")
    save_and_show(fig, "fig_01_price_series.png")


def plot_price_vs_sentiment(df: pd.DataFrame) -> None:
    fig, ax1 = plt.subplots(figsize=(14, 5))
    ax2 = ax1.twinx()

    line1 = ax1.plot(
        df["Date"],
        df["Close"],
        color="steelblue",
        alpha=0.7,
        label="Close",
    )
    line2 = ax2.plot(
        df["Date"],
        df["sentiment_score"],
        color="orange",
        alpha=0.7,
        label="Sentiment",
    )

    ax1.set_title("HSI Price vs Sentiment Score")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Close Price (HKD)", color="steelblue")
    ax2.set_ylabel("Sentiment Score", color="orange")
    lines = line1 + line2
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels, loc="upper left")
    save_and_show(fig, "fig_02_price_sentiment.png")


def plot_sentiment_distribution(df: pd.DataFrame) -> None:
    sentiment = df["sentiment_score"].dropna()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(
        sentiment,
        bins=50,
        density=True,
        alpha=0.6,
        color="steelblue",
        label="Histogram",
    )
    sentiment.plot.kde(ax=ax, color="orange", label="KDE")
    ax.set_title("Sentiment Score Distribution")
    ax.set_xlabel("Sentiment Score")
    ax.set_ylabel("Density")
    ax.legend()
    save_and_show(fig, "fig_03_sentiment_dist.png")


def plot_sentiment_vs_return(df: pd.DataFrame) -> None:
    clean = df[["sentiment_score", "return_open"]].dropna()
    if len(clean) < 2:
        raise ValueError("Not enough valid rows to build the sentiment vs return scatter plot.")

    slope, intercept, r_value, p_value, _ = stats.linregress(
        clean["sentiment_score"],
        clean["return_open"],
    )

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(clean["sentiment_score"], clean["return_open"], alpha=0.3, s=10)
    x_line = np.linspace(clean["sentiment_score"].min(), clean["sentiment_score"].max(), 100)
    ax.plot(x_line, slope * x_line + intercept, "r-", linewidth=2)
    ax.set_title(f"Sentiment vs Next-Day Return (r={r_value:.3f}, p={p_value:.3f})")
    ax.set_xlabel("Sentiment Score (t)")
    ax.set_ylabel("Return Open (t+1)")
    save_and_show(fig, "fig_04_scatter.png")


def plot_correlation_heatmap(df: pd.DataFrame) -> None:
    corr_cols = [
        "sentiment_score",
        "vote_imbalance",
        "return_open",
        "return_close",
        "sentiment_lag1",
        "sentiment_lag2",
        "sentiment_lag3",
    ]
    corr = df[corr_cols].corr(method="spearman")

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, annot=True, fmt=".3f", cmap="RdBu_r", center=0, ax=ax)
    ax.set_title("Spearman Correlation Heatmap")
    save_and_show(fig, "fig_07_correlation.png")


def run_all_plots(df: pd.DataFrame) -> None:
    plot_price_series(df)
    plot_price_vs_sentiment(df)
    plot_sentiment_distribution(df)
    plot_sentiment_vs_return(df)
    plot_correlation_heatmap(df)


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
    run_all_plots(df)


if __name__ == "__main__":
    main()
