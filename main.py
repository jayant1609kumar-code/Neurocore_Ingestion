from fastapi import FastAPI, HTTPException, Header, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator, Field
import models, database

# Initialize FastAPI app
app = FastAPI()

# Create database tables automatically upon startup
models.Base.metadata.create_all(bind=database.engine)

# Dependency to get the database session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Request Validation Schema
class AlertCreate(BaseModel):
    host: str = Field(..., min_length=1)      # Required & non-empty 
    severity: str = Field(..., min_length=1)  # Required & non-empty 
    subject: str = Field(..., min_length=1)   # Required & non-empty 
    message: str
    event_id: str
    trigger_id: str

    @validator("host", "severity", "subject", "message")
    def reject_macros(cls, v):
        # STRICTOR REJECTION: If any field contains { or } -> REJECT 
        if "{" in v or "}" in v:
            raise HTTPException(status_code=400, detail="Forbidden macro/placeholder detected")
        return v

# Endpoint 1: Ingest Alerts [cite: 41]
@app.post("/api/alerts/zabbix")
def ingest_alert(
    alert: AlertCreate, 
    x_internal_key: str = Header(None), # Security header 
    db: Session = Depends(get_db)
):
    # Check for specific security key
    if x_internal_key != "neurocore-internal-key":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Store real alert data in DB [cite: 48, 55]
    db_alert = models.Alert(**alert.dict())
    db.add(db_alert)
    db.commit()
    return {"status": "success"} # [cite: 49]

# Endpoint 2: Fetch Alerts [cite: 69]
@app.get("/api/alerts")
def fetch_alerts(db: Session = Depends(get_db)):
    # Returns only real alerts, descending by time [cite: 71, 72]
    return db.query(models.Alert).order_by(models.Alert.created_at.desc()).all()