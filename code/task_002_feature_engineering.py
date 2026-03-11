from pathlib import Path

import pandas as pd


INPUT_FILE = "hsi_clean.csv"
OUTPUT_FILE = "hsi_features.csv"
FEATURE_SUMMARY_COLUMNS = [
    "sentiment_score",
    "vote_imbalance",
    "return_open",
    "return_close",
]


def load_data(file_path: str) -> pd.DataFrame:
    print(f"Loading clean data from {file_path}...")
    df = pd.read_csv(file_path)
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date").reset_index(drop=True)
    print("Clean data loaded.")
    return df


def validate_columns(df: pd.DataFrame) -> None:
    required_columns = {"Open", "Close", "Up votes", "Down votes"}
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        missing_str = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing_str}")


def build_returns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # return_open: 隔日开盘收益率，模拟收盘前获得情绪信号并在次日开盘建仓的交易场景
    df["return_open"] = df["Open"].shift(-1) / df["Open"] - 1

    # return_close: 收盘到收盘收益率，用于与主信号目标进行对比
    df["return_close"] = df["Close"].pct_change()
    return df


def build_sentiment_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # sentiment_score: 情绪净值，正值表示多头情绪占优，负值表示空头情绪占优
    df["sentiment_score"] = df["Up votes"] - df["Down votes"]

    # vote_imbalance: 情绪强度，绝对值越大表示投票者共识越强
    df["vote_imbalance"] = df["sentiment_score"].abs()

    # extreme_bull: top 20% 情绪分位数，表示极度乐观市场状态
    q80 = df["sentiment_score"].quantile(0.8)
    df["extreme_bull"] = df["sentiment_score"] >= q80

    # extreme_bear: bottom 20% 情绪分位数，表示极度悲观市场状态
    q20 = df["sentiment_score"].quantile(0.2)
    df["extreme_bear"] = df["sentiment_score"] <= q20

    # sentiment_lag1: 前 1 日情绪信号，用于检验情绪影响是否延续到下一交易日
    df["sentiment_lag1"] = df["sentiment_score"].shift(1)

    # sentiment_lag2: 前 2 日情绪信号，用于分析更短期的信号衰减
    df["sentiment_lag2"] = df["sentiment_score"].shift(2)

    # sentiment_lag3: 前 3 日情绪信号，用于分析更进一步的信号衰减
    df["sentiment_lag3"] = df["sentiment_score"].shift(3)

    return df


def build_sentiment_quantiles(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # sentiment_quantile: 将情绪净值分成五组，用于比较不同情绪区间下的收益特征
    ranked_sentiment = df["sentiment_score"].rank(method="first")
    df["sentiment_quantile"] = pd.qcut(
        ranked_sentiment,
        q=5,
        labels=["Q1", "Q2", "Q3", "Q4", "Q5"],
    )
    return df


def print_feature_diagnostics(df: pd.DataFrame) -> None:
    print("\n=== Feature Summary Statistics ===")
    print(df[FEATURE_SUMMARY_COLUMNS].describe())

    print(f"\nExtreme bull days: {int(df['extreme_bull'].sum())}")
    print(f"Extreme bear days: {int(df['extreme_bear'].sum())}")

    print("\nSentiment quantile distribution:")
    print(df["sentiment_quantile"].value_counts(sort=False, dropna=False))


def save_data(df: pd.DataFrame, output_path: str) -> None:
    df.to_csv(output_path, index=False)
    print(f"\nFeature data saved to {output_path}")


def main() -> None:
    input_path = Path(INPUT_FILE)
    if not input_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_path.resolve()}. "
            "Run task_001_data_loading.py first to generate hsi_clean.csv."
        )

    df = load_data(str(input_path))
    validate_columns(df)
    df = build_returns(df)
    df = build_sentiment_features(df)
    df = build_sentiment_quantiles(df)
    save_data(df, OUTPUT_FILE)
    print_feature_diagnostics(df)


if __name__ == "__main__":
    main()
