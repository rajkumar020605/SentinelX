from sqlalchemy.orm import Session

from app.models.alert import Alert


def create_alert(
    db: Session,
    incident_id: int,
    title: str,
    message: str,
    severity: str,
    risk_score: int
):
    active_alert = (
        db.query(Alert)
        .filter(
            Alert.incident_id == incident_id,
            Alert.status.in_([
                "new",
                "acknowledged"
            ])
        )
        .first()
    )

    if active_alert:
        return active_alert

    alert = Alert(
        incident_id=incident_id,
        title=title,
        message=message,
        severity=severity,
        risk_score=risk_score,
        status="new"
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    return alert