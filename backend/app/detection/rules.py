from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.security_event import SecurityEvent

from app.models.threat_intelligence import ThreatIntelligence

BRUTE_FORCE_THRESHOLD = 5
BRUTE_FORCE_WINDOW_MINUTES = 10


def detect_brute_force(
    db: Session,
    source_ip: str,
    username: str | None = None
):
    current_time = datetime.now(timezone.utc)

    window_start = (
        current_time
        - timedelta(minutes=BRUTE_FORCE_WINDOW_MINUTES)
    )

    query = (
        db.query(SecurityEvent)
        .filter(
            SecurityEvent.source_ip == source_ip,
            SecurityEvent.event_type == "login_failed",
            SecurityEvent.created_at >= window_start
        )
    )

    if username:
        query = query.filter(
            SecurityEvent.username == username
        )

    failed_attempts = query.count()

    if failed_attempts >= BRUTE_FORCE_THRESHOLD:
        return {
            "detected": True,
            "rule": "BRUTE_FORCE_LOGIN",
            "severity": "high",
            "risk_score": 80,
            "message": (
                f"Possible brute-force attack detected from "
                f"{source_ip}. "
                f"{failed_attempts} failed login attempts "
                f"within {BRUTE_FORCE_WINDOW_MINUTES} minutes."
            )
        }

    return {
        "detected": False,
        "rule": "BRUTE_FORCE_LOGIN",
        "severity": "low",
        "risk_score": 0,
        "message": "No brute-force activity detected"
    }
def detect_suspicious_login(
    db: Session,
    source_ip: str,
    username: str | None = None
):
    suspicious_ips = {
        "10.0.0.99",
        "192.168.100.50"
    }

    if source_ip in suspicious_ips:
        return {
            "detected": True,
            "rule": "SUSPICIOUS_LOGIN",
            "severity": "high",
            "risk_score": 70,
            "message": (
                f"Suspicious login detected from "
                f"known suspicious IP {source_ip}."
            )
        }

    return {
        "detected": False,
        "rule": "SUSPICIOUS_LOGIN",
        "severity": "low",
        "risk_score": 0,
        "message": "No suspicious login activity detected"
    }
def detect_threat_intelligence(
    db: Session,
    source_ip: str | None = None,
    ioc_type: str | None = None,
    ioc_value: str | None = None
):
    match_type = ioc_type
    match_value = ioc_value

    if not match_type and source_ip:
        match_type = "ip"
        match_value = source_ip

    threat = (
        db.query(ThreatIntelligence)
        .filter(
            ThreatIntelligence.ioc_type == match_type,
            ThreatIntelligence.ioc_value == match_value
        )
        .first()
    )

    if threat:
        threat_level = threat.threat_level.lower()

        risk_map = {
            "low": 30,
            "medium": 50,
            "high": 70,
            "critical": 90
        }

        risk_score = risk_map.get(
            threat_level,
            50
        )

        return {
            "detected": True,
            "rule": "THREAT_INTELLIGENCE_MATCH",
            "severity": threat_level,
            "risk_score": risk_score,
            "message": (
                f"Threat intelligence match found for "
                f"{match_value}. "
                f"Threat level: {threat_level}. "
                f"Source: {threat.source or 'Unknown'}."
            )
        }

    return {
        "detected": False,
        "rule": "THREAT_INTELLIGENCE_MATCH",
        "severity": "low",
        "risk_score": 0,
        "message": "No threat intelligence match found"
    }