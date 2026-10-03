from sqlalchemy.orm import Session

from app.detection.rules import (
    detect_brute_force,
    detect_suspicious_login
)
from app.detection.risk import calculate_risk


def run_detection(
    db: Session,
    source_ip: str,
    username: str | None = None
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

    # Keep only triggered detections
    detected_rules = [
        result
        for result in results
        if result["detected"]
    ]

    # Calculate overall risk
    risk = calculate_risk(detected_rules)

    return {
        "detected": len(detected_rules) > 0,
        "total_rules_checked": len(results),
        "risk": risk,
        "detections": detected_rules
    }