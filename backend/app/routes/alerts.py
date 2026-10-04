from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.alert import Alert
from app.models.user import User
from app.schemas.alert import AlertStatusUpdate
from app.security.jwt import get_current_user
from app.services.audit_service import create_audit_log


router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"]
)


# ---------------------------------------------------------
# GET ALL ALERTS
# ---------------------------------------------------------

@router.get("/")
def get_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alerts = (
        db.query(Alert)
        .order_by(Alert.created_at.desc())
        .all()
    )

    return [
        {
            "id": alert.id,
            "incident_id": alert.incident_id,
            "title": alert.title,
            "message": alert.message,
            "severity": alert.severity,
            "risk_score": alert.risk_score,
            "status": alert.status,
            "acknowledged_by": alert.acknowledged_by,
            "resolved_by": alert.resolved_by,
            "created_at": (
                alert.created_at.isoformat()
                if alert.created_at
                else None
            ),
            "updated_at": (
                alert.updated_at.isoformat()
                if alert.updated_at
                else None
            )
        }
        for alert in alerts
    ]


# ---------------------------------------------------------
# GET SINGLE ALERT
# ---------------------------------------------------------

@router.get("/{alert_id}")
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id)
        .first()
    )

    if not alert:
        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    return {
        "id": alert.id,
        "incident_id": alert.incident_id,
        "title": alert.title,
        "message": alert.message,
        "severity": alert.severity,
        "risk_score": alert.risk_score,
        "status": alert.status,
        "acknowledged_by": alert.acknowledged_by,
        "resolved_by": alert.resolved_by,
        "created_at": (
            alert.created_at.isoformat()
            if alert.created_at
            else None
        ),
        "updated_at": (
            alert.updated_at.isoformat()
            if alert.updated_at
            else None
        )
    }


# ---------------------------------------------------------
# UPDATE ALERT STATUS
# ---------------------------------------------------------

@router.patch("/{alert_id}/status")
def update_alert_status(
    alert_id: int,
    status_data: AlertStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id)
        .first()
    )

    if not alert:
        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    old_status = alert.status
    new_status = status_data.status

    if new_status == "acknowledged":
        alert.acknowledged_by = current_user.id

    if new_status == "resolved":
        alert.resolved_by = current_user.id

        if not alert.acknowledged_by:
            alert.acknowledged_by = current_user.id

    alert.status = new_status

    db.commit()
    db.refresh(alert)

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="ALERT_STATUS_CHANGED",
        resource=f"alert:{alert_id}",
        details=(
            f"Alert status changed "
            f"from {old_status} to {new_status}"
        )
    )

    return {
        "message": "Alert status updated successfully",
        "alert_id": alert.id,
        "old_status": old_status,
        "status": alert.status,
        "updated_by": current_user.username
    }