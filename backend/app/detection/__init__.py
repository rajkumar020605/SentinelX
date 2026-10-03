from sqlalchemy.orm import Session

from app.models.security_event import SecurityEvent


def detect_brute_force(
    db: Session,
    source_ip: str,
    username: str | None = None
):
    query = (
        db.query(SecurityEvent)
        .filter(
            SecurityEvent.source_ip == source_ip,
            SecurityEvent.event_type == "login_failed"
        )
    )

    if username:
        query = query.filter(
            SecurityEvent.username == username
        )

    failed_attempts = query.count()

    if failed_attempts >= 5:
        return {
            "detected": True,
            "rule": "BRUTE_FORCE_LOGIN",
            "severity": "high",
            "risk_score": 80,
            "message": (
                f"Possible brute-force attack detected from "
                f"{source_ip}. Failed attempts: {failed_attempts}"
            )
        }

    return {
        "detected": False,
        "rule": "BRUTE_FORCE_LOGIN",
        "severity": "low",
        "risk_score": 0,
        "message": "No brute-force activity detected"
    }