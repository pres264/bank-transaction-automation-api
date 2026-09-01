import os
import re
import pdfplumber
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
pdf_path = os.path.join(PROJECT_ROOT, "data", "raw", "sample_statement.pdf")


def extract_tables_from_pdf(path):
    all_rows = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                all_rows.extend(table)
    return all_rows


raw_rows = extract_tables_from_pdf(pdf_path)

print("Total rows extracted (including header):", len(raw_rows))
print("\nFirst few rows:")
for row in raw_rows[:5]:
    print(row)

# Convert extracted rows into a DataFrame, using the first row as headers
header = raw_rows[0]
data_rows = raw_rows[1:]
df = pd.DataFrame(data_rows, columns=header)

print("\nExtracted DataFrame:")
print(df)

# --- Reuse the same date parsing logic from clean_data.py ---
def parse_messy_date(date_str):
    if pd.isnull(date_str) or date_str == "":
        return pd.NaT

    formats_to_try = [
        "%Y-%m-%d",    # 2024-01-05
        "%m/%d/%Y",    # 01/08/2024
        "%b %d %Y",    # Jan 12 2024
    ]

    for fmt in formats_to_try:
        try:
            return pd.to_datetime(date_str, format=fmt)
        except (ValueError, TypeError):
            continue

    return pd.NaT


def parse_amount(amount_str):
    if pd.isnull(amount_str) or amount_str == "":
        return None, None

    amount_str = str(amount_str).strip()

    currency = "INR"
    if amount_str.startswith("$"):
        currency = "USD"
    elif amount_str.startswith("₹"):
        currency = "INR"

    is_negative = amount_str.startswith("-") or amount_str.startswith("(")
    cleaned = re.sub(r"[^\d.]", "", amount_str)

    try:
        value = float(cleaned)
        if is_negative:
            value = -value
    except ValueError:
        value = None

    return value, currency


df["date_parsed"] = df["Date"].apply(parse_messy_date)
df[["amount_parsed", "currency"]] = df["Amount"].apply(lambda x: pd.Series(parse_amount(x)))

# Flag rows missing a description - real statements shouldn't have blank ones
df["description_missing"] = df["Description"].apply(lambda x: x.strip() == "")

print("\nParsed result:")
print(df[["Date", "date_parsed", "Description", "description_missing", "Amount", "amount_parsed", "currency", "Type"]])

print("\nDate parse failures:", df["date_parsed"].isnull().sum())
print("Amount parse failures:", df["amount_parsed"].isnull().sum())    
print("\nMissing descriptions:", df["description_missing"].sum())