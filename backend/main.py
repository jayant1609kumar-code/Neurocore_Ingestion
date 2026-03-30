from fastapi import FastAPI, HTTPException, Header, Depends
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
import json
import models
import database
from sop_engine import evaluate_alert
from models import Job

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
    
    new_alert = models.Alert(
        host=payload.get("host"),
        severity=payload.get("severity"),
        subject=payload.get("subject"),
        message=payload.get("message"),
        event_id=payload.get("event_id"),
        trigger_id=payload.get("trigger_id")
    )
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)

    decision = evaluate_alert(new_alert)
    if decision:
        new_job = Job(
            alert_id=new_alert.id,
            host=new_alert.host,
            action=decision.get("action"),
            payload=json.dumps(decision.get("payload")),
            status="pending"
        )
        db.add(new_job)
        db.commit()

    return {"status": "success", "alert_id": new_alert.id}

@app.get("/api/alerts")
def fetch_alerts(db: Session = Depends(get_db)):
    return db.query(models.Alert).order_by(models.Alert.id.desc()).limit(50).all()

@app.get("/", response_class=HTMLResponse)
def dashboard():
    try:
        with open("static/dashboard.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Dashboard not found. Ensure static/dashboard.html is inside the backend folder.</h1>"