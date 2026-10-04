from sqlalchemy.orm import Session

from app.detection.rules import (
    detect_brute_force,
    detect_suspicious_login,
    detect_threat_intelligence
)

from app.detection.risk import calculate_risk

from app.services.incident_service import (
    create_incident_from_detection
)


def run_detection(
    db: Session,
    source_ip: str,
    username: str | None = None,
    ioc_type: str | None = None,
    ioc_value: str | None = None,
    event_id: int | None = None
):
    results = []

    # Rule 1: Brute-force detection
    brute_force_result = detect_brute_force(
        db=db,
        source_ip=source_ip,
        username=username
    )

    results.append(brute_force_result)

    # Rule 2: Suspicious login detection
    suspicious_login_result = detect_suspicious_login(
        db=db,
        source_ip=source_ip,
        username=username
    )

    results.append(suspicious_login_result)

    # Rule 3: Threat intelligence detection
    threat_intelligence_result = detect_threat_intelligence(
        db=db,
        source_ip=source_ip,
        ioc_type=ioc_type,
        ioc_value=ioc_value
)

    results.append(threat_intelligence_result)

    # Keep only triggered detections
    detected_rules = [
        result
        for result in results
        if result["detected"]
    ]

    # Calculate overall risk
    risk = calculate_risk(detected_rules)

    # Create incidents for detected threats
    incidents = []

    for detection in detected_rules:
        incident = create_incident_from_detection(
            db=db,
            detection=detection,
            source_ip=source_ip,
            username=username,
    	    ioc_type=ioc_type,
            ioc_value=ioc_value,
	    event_id=event_id
)

        if incident:
            incidents.append({
                "incident_id": incident.id,
                "title": incident.title,
                "status": incident.status,
                "severity": incident.severity,
                "risk_score": incident.risk_score
            })

    return {
        "detected": len(detected_rules) > 0,
        "total_rules_checked": len(results),
        "risk": risk,
        "detections": detected_rules,
        "incidents": incidents
    }