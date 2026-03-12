from pathlib import Path

import pandas as pd


INPUT_FILE = "hsi_clean.csv"
OUTPUT_FILE = "hsi_features.csv"
TRAIN_RATIO = 0.8
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
    df["return_open"] = df["Open"].shift(-1) / df["Open"] - 1
    df["return_close"] = df["Close"].pct_change()
    return df


def build_sentiment_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["sentiment_score"] = df["Up votes"] - df["Down votes"]
    df["vote_imbalance"] = df["sentiment_score"].abs()

    split_n = int(len(df) * TRAIN_RATIO)
    train_sentiment = df["sentiment_score"].iloc[:split_n]

    df["is_train"] = False
    if split_n > 0:
        df.loc[: split_n - 1, "is_train"] = True

    q80 = train_sentiment.quantile(0.8)
    q20 = train_sentiment.quantile(0.2)
    df["extreme_bull"] = df["sentiment_score"] >= q80
    df["extreme_bear"] = df["sentiment_score"] <= q20

    df["sentiment_lag1"] = df["sentiment_score"].shift(1)
    df["sentiment_lag2"] = df["sentiment_score"].shift(2)
    df["sentiment_lag3"] = df["sentiment_score"].shift(3)
    return df


def print_feature_diagnostics(df: pd.DataFrame) -> None:
    print("\n=== Feature Summary Statistics ===")
    print(df[FEATURE_SUMMARY_COLUMNS].describe())

    print(f"\nExtreme bull days: {int(df['extreme_bull'].sum())}")
    print(f"Extreme bear days: {int(df['extreme_bear'].sum())}")
    if "is_train" in df.columns:
        print(f"Train observations: {int(df['is_train'].sum())}")
        print(f"Test observations: {int((~df['is_train']).sum())}")



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
    save_data(df, OUTPUT_FILE)
    print_feature_diagnostics(df)


if __name__ == "__main__":
    main()
