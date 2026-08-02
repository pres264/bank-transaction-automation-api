from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from database import Base


class Transaction(Base):
    __tablename__ = "transactions"
    
    original_transaction_id = Column(String, nullable=True, index=True)
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    date = Column(DateTime, nullable=True)
    transaction_type = Column(String)
    category = Column(String, index=True)
    amount = Column(Float)
    currency = Column(String)
    payment_mode = Column(String)
    location = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    notes_suspicious = Column(Boolean, default=False)
    is_anomaly = Column(Boolean, default=False)
    