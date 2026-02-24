from fastapi import FastAPI, HTTPException, Header, Depends
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse  # <--- New for Module 2
from . import models, database

app = FastAPI()

# Create the database tables
models.Base.metadata.create_all(bind=database.engine)

# Dependency for database connection
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
    
    # Macro Rejection Check
    for value in payload.values():
        if isinstance(value, str) and ("{" in value or "}" in value):
            raise HTTPException(status_code=400, detail="Macros detected")

    new_alert = models.Alert(
        host=payload.get("host"),
        severity=payload.get("severity"),
        subject=payload.get("subject")
    )
    db.add(new_alert)
    db.commit()
    return {"status": "success"}

@app.get("/api/alerts")
def fetch_alerts(db: Session = Depends(get_db)):
    return db.query(models.Alert).all()



@app.get("/", response_class=HTMLResponse)
def dashboard():
    # This reads the file from the folder you created
    return open("backend/static/dashboard.html").read()