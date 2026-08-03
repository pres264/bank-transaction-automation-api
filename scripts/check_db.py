import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.append(os.path.join(PROJECT_ROOT, "app"))

from database import SessionLocal
from models import Transaction

db = SessionLocal()

total = db.query(Transaction).count()
print("Total transactions in database:", total)

sample = db.query(Transaction).limit(5).all()
for t in sample:
    print(t.transaction_id, t.user_id, t.date, t.category, t.amount, t.currency)

anomaly_count = db.query(Transaction).filter(Transaction.is_anomaly == True).count()
print("\nTransactions currently flagged as anomaly:", anomaly_count)

db.close()