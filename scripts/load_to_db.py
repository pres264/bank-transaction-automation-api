import sys
import os
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

sys.path.append(os.path.join(PROJECT_ROOT, "app"))

from database import engine, SessionLocal, Base, db_path
from models import Transaction

Base.metadata.create_all(bind=engine)

csv_path = os.path.join(PROJECT_ROOT, "data", "processed", "cleaned_transactions.csv")

db = SessionLocal()

# Clear existing data before reloading, so this script is safely rerunnable
existing_count = db.query(Transaction).count()
if existing_count > 0:
    print(f"Clearing {existing_count} existing transactions before reload...")
    db.query(Transaction).delete()
    db.commit()

df = pd.read_csv(csv_path, parse_dates=["date"])

print("Loading", len(df), "transactions into the database...")

for _, row in df.iterrows():
    transaction = Transaction(
        transaction_id=row["transaction_id"],
        original_transaction_id=row["original_transaction_id"] if pd.notnull(row["original_transaction_id"]) else None,
        user_id=row["user_id"],
        date=row["date"] if pd.notnull(row["date"]) else None,
        transaction_type=row["transaction_type"],
        category=row["category"],
        amount=row["amount"],
        currency=row["currency"],
        payment_mode=row["payment_mode"],
        location=row["location"] if pd.notnull(row["location"]) else None,
        notes=row["notes"] if pd.notnull(row["notes"]) else None,
        notes_suspicious=bool(row["notes_suspicious"]),
    )
    db.add(transaction)

db.commit()
db.close()

print(f"Done. Database created at {db_path}")