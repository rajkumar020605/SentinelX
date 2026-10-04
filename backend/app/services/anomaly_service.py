from sqlalchemy.orm import Session
from sklearn.ensemble import IsolationForest

from app.models.security_event import SecurityEvent
from app.models.incident import Incident
from app.models.incident_event import IncidentEvent
from app.services.alert_service import create_alert


SEVERITY_SCORE = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4
}


def build_event_features(event: SecurityEvent):
    severity_score = SEVERITY_SCORE.get(
        (event.severity or "low").lower(),
        1
    )

    failed_status = 1 if (
        (event.status or "").lower() == "failed"
    ) else 0

    has_source_ip = 1 if event.source_ip else 0
    has_ioc = 1 if event.ioc_value else 0
    has_username = 1 if event.username else 0

    message_length = len(event.message or "")
    event_type_length = len(event.event_type or "")

    return [
        severity_score,
        failed_status,
        has_source_ip,
        has_ioc,
        has_username,
        message_length,
        event_type_length
    ]


def create_ml_incident(
    db: Session,
    event: SecurityEvent,
    anomaly_level: str,
    anomaly_score: float
):
    """
    Create an incident for an ML anomaly.

    Prevents duplicate incidents for the same security event.
    """

    existing_link = (
        db.query(IncidentEvent)
        .filter(
            IncidentEvent.event_id == event.id
        )
        .first()
    )

    if existing_link:
        existing_incident = (
            db.query(Incident)
            .filter(
                Incident.id == existing_link.incident_id
            )
            .first()
        )

        if existing_incident:
            return existing_incident

    if anomaly_level == "high":
        severity = "high"
        risk_score = 80
    else:
        severity = "medium"
        risk_score = 50

    incident = Incident(
        title="ML Anomaly Detected",
        description=(
            f"Isolation Forest detected an anomalous security event. "
            f"Anomaly level: {anomaly_level}. "
            f"Anomaly score: {round(anomaly_score, 4)}. "
            f"Event type: {event.event_type}."
        ),
        incident_type="ML Anomaly",
        detection_rule="ML_ANOMALY",
        source_ip=event.source_ip,
        username=event.username,
        ioc_type=event.ioc_type,
        ioc_value=event.ioc_value,
        event_id=event.id,
        severity=severity,
        risk_score=risk_score,
        status="open"
    )

    db.add(incident)
    db.commit()
    db.refresh(incident)

    db.add(
        IncidentEvent(
            incident_id=incident.id,
            event_id=event.id
        )
    )

    db.commit()

    create_alert(
        db=db,
        incident_id=incident.id,
        title="ML Anomaly Detected",
        message=(
            f"Isolation Forest detected an anomalous event "
            f"(Event ID: {event.id}). "
            f"Anomaly level: {anomaly_level}. "
            f"Risk score: {risk_score}."
        ),
        severity=severity,
        risk_score=risk_score
    )

    return incident


def detect_anomalies(db: Session, limit: int = 100):

    events = (
        db.query(SecurityEvent)
        .order_by(SecurityEvent.created_at.desc())
        .limit(limit)
        .all()
    )

    if len(events) < 5:
        return {
            "model": "IsolationForest",
            "status": "insufficient_data",
            "message": (
                "At least 5 security events are required "
                "for anomaly detection."
            ),
            "total_events_analyzed": len(events),
            "anomalies_detected": 0,
            "anomalies": [],
            "incidents_created": 0
        }

    features = [
        build_event_features(event)
        for event in events
    ]

    model = IsolationForest(
        n_estimators=100,
        contamination="auto",
        random_state=42
    )

    predictions = model.fit_predict(features)
    scores = model.decision_function(features)

    results = []
    incidents_created = []

    for event, prediction, score in zip(
        events,
        predictions,
        scores
    ):

        is_anomaly = prediction == -1

        if not is_anomaly:
            continue

        if score < -0.15:
            anomaly_level = "high"
        else:
            anomaly_level = "medium"

        incident = create_ml_incident(
            db=db,
            event=event,
            anomaly_level=anomaly_level,
            anomaly_score=float(score)
        )

        incidents_created.append({
            "incident_id": incident.id,
            "event_id": event.id,
            "severity": incident.severity,
            "risk_score": incident.risk_score
        })

        results.append({
            "event_id": event.id,
            "event_type": event.event_type,
            "source_ip": event.source_ip,
            "ioc_type": event.ioc_type,
            "ioc_value": event.ioc_value,
            "username": event.username,
            "severity": event.severity,
            "status": event.status,
            "message": event.message,
            "anomaly_score": round(float(score), 4),
            "anomaly_level": anomaly_level,
            "detection": "ML_ANOMALY",
            "incident_id": incident.id,
            "risk_score": incident.risk_score
        })

    return {
        "model": "IsolationForest",
        "status": "completed",
        "total_events_analyzed": len(events),
        "anomalies_detected": len(results),
        "incidents_created": len(incidents_created),
        "anomalies": results,
        "incidents": incidents_created
    }