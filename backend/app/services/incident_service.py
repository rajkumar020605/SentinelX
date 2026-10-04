from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.models.incident_event import IncidentEvent
from app.services.alert_service import create_alert


def create_incident_from_detection(
    db: Session,
    detection: dict,
    source_ip: str | None = None,
    username: str | None = None,
    ioc_type: str | None = None,
    ioc_value: str | None = None,
    event_id: int | None = None
):
    if not detection.get("detected"):
        return None

    rule = detection.get("rule")
    severity = detection.get("severity", "medium")
    risk_score = detection.get("risk_score", 0)
    message = detection.get("message", "")

    if not ioc_type and source_ip:
        ioc_type = "ip"
        ioc_value = source_ip

    existing_incident = (
        db.query(Incident)
        .filter(
            Incident.detection_rule == rule,
            Incident.source_ip == source_ip,
            Incident.username == username,
            Incident.ioc_type == ioc_type,
            Incident.ioc_value == ioc_value,
            Incident.status.in_([
                "open",
                "investigating"
            ])
        )
        .first()
    )

    if existing_incident:

        if event_id:
            existing_link = (
                db.query(IncidentEvent)
                .filter(
                    IncidentEvent.incident_id == existing_incident.id,
                    IncidentEvent.event_id == event_id
                )
                .first()
            )

            if not existing_link:
                db.add(
                    IncidentEvent(
                        incident_id=existing_incident.id,
                        event_id=event_id
                    )
                )
                db.commit()

        # Create/reuse active alert for existing incident
        create_alert(
            db=db,
            incident_id=existing_incident.id,
            title=f"{rule} detected",
            message=message,
            severity=severity,
            risk_score=risk_score
        )

        return existing_incident

    new_incident = Incident(
        title=f"{rule} detected",
        description=message,
        incident_type="Security Detection",
        detection_rule=rule,
        source_ip=source_ip,
        username=username,
        ioc_type=ioc_type,
        ioc_value=ioc_value,
        event_id=event_id,
        severity=severity,
        risk_score=risk_score,
        status="open"
    )

    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)

    if event_id:
        db.add(
            IncidentEvent(
                incident_id=new_incident.id,
                event_id=event_id
            )
        )
        db.commit()

    # Automatically create alert
    create_alert(
        db=db,
        incident_id=new_incident.id,
        title=f"{rule} detected",
        message=message,
        severity=severity,
        risk_score=risk_score
    )

    return new_incident