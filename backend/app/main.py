from fastapi import FastAPI
from datetime import datetime, timezone

from app.database import Base, engine
from app import models

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="SentinelX Security Platform",
    description="AI-Assisted Security Monitoring and Incident Response Platform",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "application": "SentinelX",
        "message": "Security Monitoring Platform is running",
        "status": "online"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SentinelX API",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }