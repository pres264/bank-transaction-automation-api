from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TransactionResponse(BaseModel):
    transaction_id: str
    user_id: str
    date: Optional[datetime]
    transaction_type: str
    category: str
    amount: Optional[float]
    currency: Optional[str]
    payment_mode: str
    location: Optional[str]
    notes: Optional[str]
    is_anomaly: bool
    data_complete: bool

    class Config:
        from_attributes = True