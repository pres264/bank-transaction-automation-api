import pandas as pd
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

df = pd.read_csv("../data/raw/budgetwise_synthetic_dirty.csv")

print("Shape:", df.shape)
print("\nColumn names:")
print(df.columns.tolist())
print("\nFirst 10 rows:")
print("\nFirst 15 rows, key columns only:")
print(df[["date", "transaction_type", "category", "amount", "payment_mode"]].head(15))

print("\nUnique transaction_type values:")
print(df["transaction_type"].unique())

print("\nUnique category values:")
print(df["category"].unique())

print("\nUnique payment_mode values:")
print(df["payment_mode"].unique())

print("\nSample of 'amount' column (raw strings):")
print(df["amount"].head(20).tolist())

print("\nSample of 'date' column (raw strings):")
print(df["date"].head(20).tolist())
print("\nData types:")
print(df.dtypes)