from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db
from models import Transaction
from schemas import TransactionResponse
from config import settings
from typing import List

app = FastAPI(title="Bank Transaction Automation API")


def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/health")
def health_check():
    return {"status": "ok"}

from typing import Optional
from datetime import datetime

@app.get("/transactions", response_model=List[TransactionResponse])
def get_transactions(
    db: Session = Depends(get_db),
    _: None = Depends(verify_api_key),
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
    category: Optional[str] = None,
    currency: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    query = db.query(Transaction)

    if user_id:
        query = query.filter(Transaction.user_id == user_id)
    if category:
        query = query.filter(Transaction.category == category)
    if currency:
        query = query.filter(Transaction.currency == currency)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)

    transactions = query.offset(skip).limit(min(limit, 500)).all()
    return transactions


from sqlalchemy import func

@app.get("/transactions/summary")
def get_summary(
    db: Session = Depends(get_db),
    _: None = Depends(verify_api_key),
    user_id: Optional[str] = None,
):
    query = db.query(
        Transaction.category,
        Transaction.currency,
        Transaction.transaction_type,
        func.count(Transaction.id).label("count"),
        func.sum(Transaction.amount).label("total_amount"),
        func.avg(Transaction.amount).label("average_amount"),
    ).filter(Transaction.data_complete == True)

    if user_id:
        query = query.filter(Transaction.user_id == user_id)

    results = query.group_by(
        Transaction.category, Transaction.currency, Transaction.transaction_type
    ).all()

    summary = [
        {
            "category": r.category,
            "currency": r.currency,
            "transaction_type": r.transaction_type,
            "count": r.count,
            "total_amount": round(r.total_amount, 2),
            "average_amount": round(r.average_amount, 2),
        }
        for r in results
    ]

    return {"user_id": user_id, "summary": summary}

@app.get("/transactions/anomalies", response_model=List[TransactionResponse])
def get_anomalies(
    db: Session = Depends(get_db),
    _: None = Depends(verify_api_key),
    user_id: Optional[str] = None,
):
    query = db.query(Transaction).filter(Transaction.is_anomaly == True)

    if user_id:
        query = query.filter(Transaction.user_id == user_id)

    return query.all()