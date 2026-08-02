import sys
import os
import pandas as pd

# Add the app/ folder to Python's search path so we can import from it
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "app"))

from database import engine, SessionLocal, Base
from models import Transaction

# Create the actual database file and table structure
Base.metadata.create_all(bind=engine)

df = pd.read_csv("../data/processed/cleaned_transactions.csv", parse_dates=["date"])

print("Loading", len(df), "transactions into the database...")

db = SessionLocal()

for _, row in df.iterrows():
    transaction = Transaction(
        transaction_id=row["transaction_id"],
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

print("Done. Database created at app/transactions.db")