import sys
import os
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.append(os.path.join(PROJECT_ROOT, "app"))

from database import SessionLocal
from models import Transaction

db = SessionLocal()

# Pull only complete, expense-type transactions into a dataframe for analysis -
# anomalies are most meaningful for expenses (unusually large spending),
# and incomplete records can't be trusted for this calculation anyway
transactions = db.query(Transaction).filter(
    Transaction.data_complete == True,
    Transaction.transaction_type == "Expense"
).all()

data = [{
    "id": t.id,
    "user_id": t.user_id,
    "category": t.category,
    "currency": t.currency,
    "amount": t.amount,
} for t in transactions]

df = pd.DataFrame(data)
print("Analyzing", len(df), "expense transactions...")

# Calculate mean and std dev PER user, per category, per currency -
# this is the key design decision: "unusual" is relative to that specific
# person's own normal spending pattern in that specific context, not a
# blanket threshold across everyone
group_stats = df.groupby(["user_id", "category", "currency"])["amount"].agg(
    ["mean", "std", "count"]
).reset_index()

# A group needs at least a handful of transactions before "unusual" is
# statistically meaningful - flag nothing for sparse groups
group_stats = group_stats[group_stats["count"] >= 4]

df = df.merge(group_stats, on=["user_id", "category", "currency"], how="left")

# Flag anything more than 3 standard deviations above that group's mean
df["threshold"] = df["mean"] + (3 * df["std"])
df["is_anomaly"] = (df["amount"] > df["threshold"]) & df["threshold"].notnull()

anomaly_count = df["is_anomaly"].sum()
print("Anomalies detected:", anomaly_count)
print("\nSample flagged anomalies:")
print(df[df["is_anomaly"]][["user_id", "category", "amount", "mean", "threshold"]].head(10))

# Write the flags back to the database
anomaly_ids = df[df["is_anomaly"]]["id"].tolist()
db.query(Transaction).filter(Transaction.id.in_(anomaly_ids)).update(
    {Transaction.is_anomaly: True}, synchronize_session=False
)
db.commit()
db.close()

print(f"\nUpdated {len(anomaly_ids)} transactions as anomalies in the database.")