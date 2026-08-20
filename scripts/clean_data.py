import os
import re
import pandas as pd
from rapidfuzz import process, fuzz

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

RAW_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "budgetwise_synthetic_dirty.csv")
PROCESSED_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "cleaned_transactions.csv")

df = pd.read_csv(RAW_PATH)

print("Original shape:", df.shape)

# ---- Duplicate transaction_id handling ----
print("\nDuplicate transaction_id check:")
dupe_ids = df[df.duplicated(subset=["transaction_id"], keep=False)]
print("Total rows involved in duplicates:", len(dupe_ids))
print("Unique duplicated IDs:", dupe_ids["transaction_id"].nunique())

before_dedup = len(df)
df = df.drop_duplicates(subset=[c for c in df.columns if c != "transaction_id"] + ["transaction_id"])
print(f"\nRemoved {before_dedup - len(df)} true duplicate rows (identical in every column)")

remaining_dupes = df[df.duplicated(subset=["transaction_id"], keep=False)]
print("Remaining ID collisions (different transactions sharing an ID):", remaining_dupes["transaction_id"].nunique())

df["original_transaction_id"] = df["transaction_id"]

dupe_mask = df.duplicated(subset=["transaction_id"], keep=False)
occurrence_number = df.groupby("transaction_id").cumcount() + 1

df.loc[dupe_mask, "transaction_id"] = (
    df.loc[dupe_mask, "transaction_id"] + "-" + occurrence_number[dupe_mask].astype(str)
)

print("Final unique transaction_id count:", df["transaction_id"].nunique())
print("Final row count:", len(df))

# ---- Date parsing ----
print("\nMissing dates:", df["date"].isnull().sum())


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

    return pd.NaT


df["date_parsed"] = df["date"].apply(parse_messy_date)

print("\nRows where date parsing failed (excluding originally-missing):")
failed = df[df["date_parsed"].isnull() & df["date"].notnull()]
print(failed[["date"]].head(20))
print("\nTotal parse failures:", len(failed))

# ---- Amount parsing (currency-aware) ----


def parse_amount(amount_str):
    if pd.isnull(amount_str):
        return pd.Series([None, None])

    amount_str = str(amount_str).strip()

    currency = "INR"  # default assumption, since all locations are Indian cities
    if amount_str.startswith("$"):
        currency = "USD"
    elif amount_str.startswith("₹"):
        currency = "INR"

    cleaned = re.sub(r"[^\d.\-]", "", amount_str)

    try:
        value = float(cleaned)
    except ValueError:
        value = None

    return pd.Series([value, currency])


df[["amount_parsed", "amount_currency"]] = df["amount"].apply(parse_amount)

print("\nAmount parsing check:")
print(df[["amount", "amount_parsed", "amount_currency"]].head(20))

print("\nCurrency distribution:")
print(df["amount_currency"].value_counts())

failed_amounts = df[df["amount_parsed"].isnull() & df["amount"].notnull()]
print("\nRows where amount parsing failed:")
print(failed_amounts[["amount"]].head(10))
print("Total amount parse failures:", len(failed_amounts))

# Finalize cleaned core columns
df["amount"] = df["amount_parsed"]
df["currency"] = df["amount_currency"]
df["date"] = df["date_parsed"]
df = df.drop(columns=["amount_parsed", "amount_currency", "date_parsed"])

print("\nFinal columns:", df.columns.tolist())
print("\nCurrency-aware summary (sum by currency):")
print(df.groupby("currency")["amount"].agg(["count", "sum", "mean"]).round(2))

# ---- Category cleanup (fuzzy matching) ----
canonical_categories = [
    "Rent", "Food", "Entertainment", "Savings", "Education",
    "Others", "Salary", "Other Income", "Travel", "Health",
    "Utilities", "Shopping", "Bonus"
]

canonical_payment_modes = ["Cash", "Card", "UPI", "Bank Transfer"]


def fuzzy_clean(value, canonical_list, threshold=80):
    if pd.isnull(value):
        return None
    match, score, _ = process.extractOne(value, canonical_list, scorer=fuzz.ratio)
    if score >= threshold:
        return match
    return value


df["category_clean"] = df["category"].apply(lambda x: fuzzy_clean(x, canonical_categories, threshold=75))

print("\nCategory cleanup results:")
print("Original unique categories:", df["category"].nunique())
print("Cleaned unique categories:", df["category_clean"].nunique())
print(df["category_clean"].value_counts())

unmatched = df[~df["category_clean"].isin(canonical_categories) & df["category_clean"].notnull()]
print("\nRows where category didn't confidently match anything (need review):")
print(unmatched["category"].unique())

# ---- Payment mode cleanup (fuzzy matching) ----
print("\n--- PAYMENT MODE CLEANUP ---")
df["payment_mode_clean"] = df["payment_mode"].apply(
    lambda x: fuzzy_clean(x, canonical_payment_modes, threshold=65)
)

print("Original unique payment modes:", df["payment_mode"].nunique())
print("Cleaned unique payment modes:", df["payment_mode_clean"].nunique())
print(df["payment_mode_clean"].value_counts())

unmatched_payments = df[~df["payment_mode_clean"].isin(canonical_payment_modes) & df["payment_mode_clean"].notnull()]
print("\nUnmatched payment mode values:")
print(unmatched_payments["payment_mode"].unique())

# Finalize cleaned categorical columns
df["category"] = df["category_clean"]
df["payment_mode"] = df["payment_mode_clean"]
df = df.drop(columns=["category_clean", "payment_mode_clean"])

# ---- Handle genuinely missing category / payment_mode / amount / currency ----
df["category"] = df["category"].fillna("Uncategorized")
df["payment_mode"] = df["payment_mode"].fillna("Unknown")

df["data_complete"] = df["amount"].notnull() & df["currency"].notnull()
print("\nIncomplete records (missing amount/currency):", (~df["data_complete"]).sum())

# ---- Flag suspicious/garbage notes ----
df["notes_suspicious"] = df["notes"].apply(
    lambda x: bool(re.match(r"^[A-Za-z0-9]{15,}$", str(x))) if pd.notnull(x) else False
)
print("\nSuspicious notes flagged:", df["notes_suspicious"].sum())

# ---- Save ----
df.to_csv(PROCESSED_PATH, index=False)
print("\nFinal shape:", df.shape)
print("Saved to", PROCESSED_PATH)