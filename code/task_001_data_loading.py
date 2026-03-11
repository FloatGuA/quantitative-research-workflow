from pathlib import Path

import numpy as np
import pandas as pd


DATA_FILE = "HSI.xlsx"
OUTPUT_FILE = "hsi_clean.csv"
VOTE_TOLERANCE = 1e-6
SUMMARY_COLUMNS = ["Open", "High", "Low", "Close", "Up votes", "Down votes"]


def load_data(file_path: str) -> pd.DataFrame:
    print(f"Loading data from {file_path}...")
    df = pd.read_excel(file_path)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    print("Data loaded and sorted by Date.")
    return df


def inspect_data(df: pd.DataFrame) -> pd.DataFrame:
    print("\n=== Data Inspection ===")
    print(f"Shape: {df.shape}")
    print("\nColumn dtypes:")
    print(df.dtypes)

    print("\nMissing values by column:")
    print(df.isna().sum())

    duplicate_count = df.duplicated().sum()
    print(f"\nDuplicate rows: {duplicate_count}")

    df = df.copy()
    df["vote_sum"] = df["Up votes"] + df["Down votes"]
    df["vote_anomaly"] = (df["vote_sum"] - 1).abs() > VOTE_TOLERANCE
    anomaly_count = int(df["vote_anomaly"].sum())
    print(f"Vote sum anomaly rows: {anomaly_count}")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    print("\n=== Data Cleaning ===")
    df = df.copy()

    before_missing = df[["Up votes", "Down votes"]].isna().sum()
    print("Missing sentiment values before forward fill:")
    print(before_missing)

    df["Up votes"] = df["Up votes"].ffill()
    df["Down votes"] = df["Down votes"].ffill()

    after_missing = df[["Up votes", "Down votes"]].isna().sum()
    print("\nMissing sentiment values after forward fill:")
    print(after_missing)

    remaining_nans = int(after_missing.sum())
    print(f"Remaining NaN in sentiment columns: {remaining_nans}")
    return df


def summarize_data(df: pd.DataFrame) -> pd.DataFrame:
    print("\n=== Summary Statistics ===")
    available_columns = [column for column in SUMMARY_COLUMNS if column in df.columns]
    if not available_columns:
        raise ValueError("No expected numeric columns found for summary statistics.")

    summary = df[available_columns].describe()
    print(summary)
    return summary


def save_data(df: pd.DataFrame, output_path: str) -> None:
    print("\n=== Save Clean Data ===")
    df.to_csv(output_path, index=False)
    print(f"Clean data saved to {output_path}")
    print(f"Final shape: {df.shape}")


def main() -> None:
    data_path = Path(DATA_FILE)
    if not data_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {data_path.resolve()}. "
            "Place HSI.xlsx in the working directory before running this script."
        )

    df = load_data(str(data_path))
    df = inspect_data(df)
    df = clean_data(df)
    summarize_data(df)
    save_data(df, OUTPUT_FILE)


if __name__ == "__main__":
    main()
