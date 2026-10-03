from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.security_event import SecurityEvent
from app.schemas.security_event import SecurityEventCreate
from app.models.user import User
from app.security.jwt import get_current_user


router = APIRouter(
    prefix="/security-events",
    tags=["Security Events"]
)


@router.post("/")
def create_security_event(
    event_data: SecurityEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_event = SecurityEvent(
        event_type=event_data.event_type,
        source_ip=event_data.source_ip,
        username=event_data.username,
        action=event_data.action,
        status=event_data.status,
        severity=event_data.severity,
        message=event_data.message
    )

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return {
        "message": "Security event recorded successfully",
        "event_id": new_event.id,
        "event_type": new_event.event_type,
        "severity": new_event.severity,
        "created_by": current_user.username
    }
@router.get("/")
def get_security_events(
    event_type: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    status: str | None = Query(default=None),
    source_ip: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(SecurityEvent)

    if event_type:
        query = query.filter(
            SecurityEvent.event_type == event_type
        )

    if severity:
        query = query.filter(
            SecurityEvent.severity == severity
        )

    if status:
        query = query.filter(
            SecurityEvent.status == status
        )

    if source_ip:
        query = query.filter(
            SecurityEvent.source_ip == source_ip
        )

    events = (
        query
        .order_by(SecurityEvent.created_at.desc())
        .all()
    )

    return [
        {
            "id": event.id,
            "event_type": event.event_type,
            "source_ip": event.source_ip,
            "username": event.username,
            "action": event.action,
            "status": event.status,
            "severity": event.severity,
            "message": event.message,
            "created_at": (
                event.created_at.isoformat()
                if event.created_at else None
            )
        }
        for event in events
    ]