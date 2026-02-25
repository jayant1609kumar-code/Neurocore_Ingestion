from fastapi import FastAPI, HTTPException, Header, Depends
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from . import models, database
import json
from .sop_engine import evaluate_alert
from .models import Job

app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/alerts/zabbix")
async def ingest_alert(payload: dict, x_internal_key: str = Header(None), db: Session = Depends(get_db)):
    if x_internal_key != "neurocore-internal-key":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    for value in payload.values():
        if isinstance(value, str) and ("{" in value or "}" in value):
            raise HTTPException(status_code=400, detail="Macros detected")

    new_alert = models.Alert(
        host=payload.get("host"),
        severity=payload.get("severity"),
        subject=payload.get("subject"),
        message=payload.get("message")
    )
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)

    decision = evaluate_alert(new_alert)

    if decision:
        new_job = Job(
            alert_id=new_alert.id,
            host=new_alert.host,
            action=decision["action"],
            payload=json.dumps(decision["payload"]),
            status="pending"
        )
        db.add(new_job)
        db.commit()

    return {"status": "success", "alert_id": new_alert.id}

@app.get("/api/alerts")
def fetch_alerts(db: Session = Depends(get_db)):
    return db.query(models.Alert).order_by(models.Alert.id.desc()).all()

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return open("backend/static/dashboard.html").read()