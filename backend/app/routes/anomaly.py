from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.security.jwt import get_current_user
from app.services.anomaly_service import detect_anomalies


router = APIRouter(
    prefix="/anomaly",
    tags=["AI Anomaly Detection"]
)


@router.get("/scan")
def scan_for_anomalies(
    limit: int = Query(
        default=100,
        ge=5,
        le=1000
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = detect_anomalies(
        db=db,
        limit=limit
    )

    result["generated_for"] = (
        current_user.username
    )

    return result