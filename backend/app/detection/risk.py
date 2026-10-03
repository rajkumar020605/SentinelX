def calculate_risk(detections: list[dict]):
    if not detections:
        return {
            "risk_score": 0,
            "risk_level": "low"
        }

    highest_score = max(
        detection["risk_score"]
        for detection in detections
    )

    if highest_score >= 90:
        risk_level = "critical"
    elif highest_score >= 70:
        risk_level = "high"
    elif highest_score >= 40:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        "risk_score": highest_score,
        "risk_level": risk_level
    }