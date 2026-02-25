from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from datetime import datetime
from .database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    host = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    message = Column(String)
    event_id = Column(String)
    trigger_id = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id")) 
    host = Column(String)
    action = Column(String) 
    payload = Column(String) 
    status = Column(String, default="pending") 
    created_at = Column(DateTime, default=datetime.utcnow)