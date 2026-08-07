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


@app.get("/transactions", response_model=List[TransactionResponse])
def get_transactions(
    db: Session = Depends(get_db),
    _: None = Depends(verify_api_key)
):
    transactions = db.query(Transaction).limit(100).all()
    return transactions