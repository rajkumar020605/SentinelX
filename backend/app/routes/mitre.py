from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.incident import Incident
from app.security.jwt import get_current_user
from app.services.mitre_service import (
    get_mitre_mapping,
    get_all_mitre_mappings
)


router = APIRouter(
    prefix="/mitre",
    tags=["MITRE ATT&CK"]
)


@router.get("/techniques")
def get_mitre_techniques(
    current_user: User = Depends(get_current_user)
):
    return {
        "total_mappings": len(
            get_all_mitre_mappings()
        ),
        "mappings": get_all_mitre_mappings()
    }


@router.get("/rule/{detection_rule}")
def get_mitre_for_rule(
    detection_rule: str,
    current_user: User = Depends(get_current_user)
):
    mapping = get_mitre_mapping(detection_rule)

    if not mapping:
        return {
            "detection_rule": detection_rule,
            "mapped": False,
            "message": (
                "No direct MITRE ATT&CK mapping "
                "is currently defined for this rule."
            )
        }

    return {
        "detection_rule": detection_rule,
        "mapped": True,
        "mitre": mapping
    }


@router.get("/incident/{incident_id}")
def get_mitre_for_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    mapping = get_mitre_mapping(
        incident.detection_rule
    )

    if not mapping:
        return {
            "incident_id": incident.id,
            "detection_rule": incident.detection_rule,
            "mapped": False,
            "message": (
                "No direct MITRE ATT&CK mapping "
                "is currently defined for this incident."
            )
        }

    return {
        "incident_id": incident.id,
        "title": incident.title,
        "detection_rule": incident.detection_rule,
        "severity": incident.severity,
        "risk_score": incident.risk_score,
        "status": incident.status,
        "mapped": True,
        "mitre": mapping
    }