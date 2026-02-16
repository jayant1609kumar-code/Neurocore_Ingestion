from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.sql import func
from database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    host = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    message = Column(String)
    event_id = Column(String)
    trigger_id = Column(String)
    # Automatically saves the time in UTC as required
    created_at = Column(DateTime(timezone=True), server_default=func.now())