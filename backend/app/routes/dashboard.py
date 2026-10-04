from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.security_event import SecurityEvent
from app.models.incident import Incident
from app.models.alert import Alert
from app.models.user import User
from app.security.jwt import get_current_user


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # -----------------------------
    # Total counts
    # -----------------------------

    total_events = db.query(
        func.count(SecurityEvent.id)
    ).scalar()

    total_incidents = db.query(
        func.count(Incident.id)
    ).scalar()

    total_alerts = db.query(
        func.count(Alert.id)
    ).scalar()

    # -----------------------------
    # Incident status counts
    # -----------------------------

    open_incidents = db.query(
        func.count(Incident.id)
    ).filter(
        Incident.status == "open"
    ).scalar()

    investigating_incidents = db.query(
        func.count(Incident.id)
    ).filter(
        Incident.status == "investigating"
    ).scalar()

    resolved_incidents = db.query(
        func.count(Incident.id)
    ).filter(
        Incident.status.in_(["resolved", "closed"])
    ).scalar()

    # -----------------------------
    # Incident severity counts
    # -----------------------------

    critical_incidents = db.query(
        func.count(Incident.id)
    ).filter(
        Incident.severity == "critical"
    ).scalar()

    high_incidents = db.query(
        func.count(Incident.id)
    ).filter(
        Incident.severity == "high"
    ).scalar()

    medium_incidents = db.query(
        func.count(Incident.id)
    ).filter(
        Incident.severity == "medium"
    ).scalar()

    low_incidents = db.query(
        func.count(Incident.id)
    ).filter(
        Incident.severity == "low"
    ).scalar()

    # -----------------------------
    # Alert status counts
    # -----------------------------

    new_alerts = db.query(
        func.count(Alert.id)
    ).filter(
        Alert.status == "new"
    ).scalar()

    acknowledged_alerts = db.query(
        func.count(Alert.id)
    ).filter(
        Alert.status == "acknowledged"
    ).scalar()

    resolved_alerts = db.query(
        func.count(Alert.id)
    ).filter(
        Alert.status == "resolved"
    ).scalar()

    # -----------------------------
    # Recent security events
    # -----------------------------

    recent_events = (
        db.query(SecurityEvent)
        .order_by(
            SecurityEvent.created_at.desc()
        )
        .limit(10)
        .all()
    )

    recent_event_list = [
        {
            "event_id": event.id,
            "event_type": event.event_type,
            "source_ip": event.source_ip,
            "ioc_type": event.ioc_type,
            "ioc_value": event.ioc_value,
            "username": event.username,
            "severity": event.severity,
            "status": event.status,
            "message": event.message,
            "created_at": (
                event.created_at.isoformat()
                if event.created_at
                else None
            )
        }
        for event in recent_events
    ]

    # -----------------------------
    # Recent incidents
    # -----------------------------

    recent_incidents = (
        db.query(Incident)
        .order_by(
            Incident.created_at.desc()
        )
        .limit(10)
        .all()
    )

    recent_incident_list = [
        {
            "incident_id": incident.id,
            "title": incident.title,
            "incident_type": incident.incident_type,
            "detection_rule": incident.detection_rule,
            "severity": incident.severity,
            "risk_score": incident.risk_score,
            "status": incident.status,
            "source_ip": incident.source_ip,
            "username": incident.username,
            "created_at": (
                incident.created_at.isoformat()
                if incident.created_at
                else None
            )
        }
        for incident in recent_incidents
    ]

    # -----------------------------
    # Recent alerts
    # -----------------------------

    recent_alerts = (
        db.query(Alert)
        .order_by(
            Alert.created_at.desc()
        )
        .limit(10)
        .all()
    )

    recent_alert_list = [
        {
            "alert_id": alert.id,
            "incident_id": alert.incident_id,
            "title": alert.title,
            "severity": alert.severity,
            "risk_score": alert.risk_score,
            "status": alert.status,
            "created_at": (
                alert.created_at.isoformat()
                if alert.created_at
                else None
            )
        }
        for alert in recent_alerts
    ]

    return {
        "dashboard": {
            "total_security_events": total_events,
            "total_incidents": total_incidents,
            "total_alerts": total_alerts
        },

        "incident_status": {
            "open": open_incidents,
            "investigating": investigating_incidents,
            "resolved_or_closed": resolved_incidents
        },

        "incident_severity": {
            "critical": critical_incidents,
            "high": high_incidents,
            "medium": medium_incidents,
            "low": low_incidents
        },

        "alert_status": {
            "new": new_alerts,
            "acknowledged": acknowledged_alerts,
            "resolved": resolved_alerts
        },

        "recent_events": recent_event_list,
        "recent_incidents": recent_incident_list,
        "recent_alerts": recent_alert_list,

        "generated_for": current_user.username
    }