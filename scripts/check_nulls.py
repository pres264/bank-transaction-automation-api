import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.append(os.path.join(PROJECT_ROOT, "app"))

from database import SessionLocal
from models import Transaction

db = SessionLocal()

print("Transactions with missing category:")
print(db.query(Transaction).filter(Transaction.category == None).count())

print("Transactions with missing payment_mode:")
print(db.query(Transaction).filter(Transaction.payment_mode == None).count())

print("Transactions with missing amount:")
print(db.query(Transaction).filter(Transaction.amount == None).count())

print("Transactions with missing currency:")
print(db.query(Transaction).filter(Transaction.currency == None).count())

# Show one actual example row with a missing value
example = db.query(Transaction).filter(Transaction.category == None).first()
if example:
    print("\nExample row with missing category:")
    print(example.transaction_id, example.original_transaction_id, example.amount, example.notes)

db.close()

import pandas as pd

raw_df = pd.read_csv(os.path.join(PROJECT_ROOT, "data", "raw", "budgetwise_synthetic_dirty.csv"))

print("\nChecking raw data for transaction T11066:")
print(raw_df[raw_df["transaction_id"] == "T11066"])

print("\nRaw data null counts:")
print(raw_df[["category", "payment_mode", "amount"]].isnull().sum())