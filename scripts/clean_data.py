import pandas as pd

df = pd.read_csv("../data/raw/budgetwise_synthetic_dirty.csv")

print("Original shape:", df.shape)
print("Missing dates:", df["date"].isnull().sum())


def parse_messy_date(date_str):
    if pd.isnull(date_str):
        return pd.NaT

    formats_to_try = [
        "%B %d %Y",    # December 22 2021
        "%m/%d/%Y",    # 03/24/2022
        "%m-%d-%y",    # 12-07-22 (assumed MM-DD-YY)
        "%Y-%m-%d",    # 2022-01-06
        "%d-%m-%y",    # 19-11-21 (DD-MM-YY - only matches when day > 12)
        "%d/%m/%y",    # 29/10/19 (DD/MM/YY - only matches when day > 12)
        "%Y/%m/%d",    # 2020/11/17 (ISO order, slash separator)
    ]

    for fmt in formats_to_try:
        try:
            return pd.to_datetime(date_str, format=fmt)
        except (ValueError, TypeError):
            continue

    return pd.NaT  # none of the formats matched


df["date_parsed"] = df["date"].apply(parse_messy_date)

print("\nRows where date parsing failed (excluding originally-missing):")
failed = df[df["date_parsed"].isnull() & df["date"].notnull()]
print(failed[["date"]].head(20))
print("\nTotal parse failures:", len(failed))