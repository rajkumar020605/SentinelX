from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.incident import Incident
from app.models.incident_event import IncidentEvent
from app.models.security_event import SecurityEvent
from app.models.user import User

from app.schemas.incident import (
    IncidentCreate,
    IncidentStatusUpdate,
    InvestigationUpdate,
    IncidentAssignment
)

from app.security.jwt import get_current_user
from app.services.audit_service import create_audit_log


router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"]
)


# ---------------------------------------------------------
# CREATE INCIDENT
# ---------------------------------------------------------

@router.post("/")
def create_incident(
    incident_data: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_incident = Incident(
        title=incident_data.title,
        description=incident_data.description,
        incident_type=incident_data.incident_type,
        detection_rule=incident_data.detection_rule,
        source_ip=incident_data.source_ip,
        username=incident_data.username,
        severity=incident_data.severity,
        risk_score=incident_data.risk_score,
        status="open"
    )

    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="INCIDENT_CREATED",
        resource=f"incident:{new_incident.id}",
        details=f"Incident created: {new_incident.title}"
    )

    return {
        "message": "Incident created successfully",
        "incident_id": new_incident.id,
        "title": new_incident.title,
        "severity": new_incident.severity,
        "risk_score": new_incident.risk_score,
        "status": new_incident.status,
        "created_by": current_user.username
    }


# ---------------------------------------------------------
# GET ALL INCIDENTS
# ---------------------------------------------------------

@router.get("/")
def get_incidents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    incidents = (
        db.query(Incident)
        .order_by(Incident.created_at.desc())
        .all()
    )

    return [
        {
            "id": incident.id,
            "title": incident.title,
            "description": incident.description,
            "incident_type": incident.incident_type,
            "detection_rule": incident.detection_rule,
            "source_ip": incident.source_ip,
            "ioc_type": incident.ioc_type,
            "ioc_value": incident.ioc_value,
            "event_id": incident.event_id,
            "username": incident.username,
            "severity": incident.severity,
            "risk_score": incident.risk_score,
            "status": incident.status,
            "assigned_to": incident.assigned_to,
            "investigation_notes": incident.investigation_notes,
            "created_at": (
                incident.created_at.isoformat()
                if incident.created_at
                else None
            ),
            "updated_at": (
                incident.updated_at.isoformat()
                if incident.updated_at
                else None
            )
        }
        for incident in incidents
    ]


# ---------------------------------------------------------
# GET SINGLE INCIDENT
# ---------------------------------------------------------

@router.get("/{incident_id}")
def get_incident(
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

    return {
        "id": incident.id,
        "title": incident.title,
        "description": incident.description,
        "incident_type": incident.incident_type,
        "detection_rule": incident.detection_rule,
        "source_ip": incident.source_ip,
        "ioc_type": incident.ioc_type,
        "ioc_value": incident.ioc_value,
        "event_id": incident.event_id,
        "username": incident.username,
        "severity": incident.severity,
        "risk_score": incident.risk_score,
        "status": incident.status,
        "assigned_to": incident.assigned_to,
        "investigation_notes": incident.investigation_notes,
        "created_at": (
            incident.created_at.isoformat()
            if incident.created_at
            else None
        ),
        "updated_at": (
            incident.updated_at.isoformat()
            if incident.updated_at
            else None
        )
    }


# ---------------------------------------------------------
# UPDATE INCIDENT STATUS
# ---------------------------------------------------------

@router.patch("/{incident_id}/status")
def update_incident_status(
    incident_id: int,
    status_data: IncidentStatusUpdate,
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

    old_status = incident.status

    incident.status = status_data.status

    db.commit()
    db.refresh(incident)

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="INCIDENT_STATUS_CHANGED",
        resource=f"incident:{incident_id}",
        details=(
            f"Incident status changed "
            f"from {old_status} to {incident.status}"
        )
    )

    return {
        "message": "Incident status updated successfully",
        "incident_id": incident.id,
        "old_status": old_status,
        "status": incident.status,
        "updated_by": current_user.username
    }


# ---------------------------------------------------------
# UPDATE INVESTIGATION NOTES
# ---------------------------------------------------------

@router.patch("/{incident_id}/investigation")
def update_investigation(
    incident_id: int,
    investigation_data: InvestigationUpdate,
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

    incident.investigation_notes = (
        investigation_data.investigation_notes
    )

    db.commit()
    db.refresh(incident)

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="INVESTIGATION_UPDATED",
        resource=f"incident:{incident_id}",
        details="Investigation notes updated"
    )

    return {
        "message": "Investigation notes updated successfully",
        "incident_id": incident.id,
        "investigation_notes": incident.investigation_notes,
        "updated_by": current_user.username
    }


# ---------------------------------------------------------
# ASSIGN INCIDENT
# ---------------------------------------------------------

@router.patch("/{incident_id}/assign")
def assign_incident(
    incident_id: int,
    assignment_data: IncidentAssignment,
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

    assigned_user = (
        db.query(User)
        .filter(User.id == assignment_data.assigned_to)
        .first()
    )

    if not assigned_user:
        raise HTTPException(
            status_code=404,
            detail="Assigned user not found"
        )

    if not assigned_user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Cannot assign incident to inactive user"
        )

    incident.assigned_to = assigned_user.id

    db.commit()
    db.refresh(incident)

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="INCIDENT_ASSIGNED",
        resource=f"incident:{incident_id}",
        details=(
            f"Incident assigned to user "
            f"{assigned_user.username}"
        )
    )

    return {
        "message": "Incident assigned successfully",
        "incident_id": incident.id,
        "assigned_to": assigned_user.id,
        "assigned_username": assigned_user.username,
        "assigned_role": assigned_user.role,
        "assigned_by": current_user.username
    }


# ---------------------------------------------------------
# GET INCIDENT EVENTS / EVIDENCE
# ---------------------------------------------------------

@router.get("/{incident_id}/events")
def get_incident_events(
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

    evidence = (
        db.query(IncidentEvent, SecurityEvent)
        .join(
            SecurityEvent,
            IncidentEvent.event_id == SecurityEvent.id
        )
        .filter(
            IncidentEvent.incident_id == incident_id
        )
        .order_by(
            IncidentEvent.created_at.desc()
        )
        .all()
    )

    return [
        {
            "event_id": event.id,
            "event_type": event.event_type,
            "source_ip": event.source_ip,
            "ioc_type": event.ioc_type,
            "ioc_value": event.ioc_value,
            "username": event.username,
            "action": event.action,
            "status": event.status,
            "severity": event.severity,
            "message": event.message,
            "created_at": (
                event.created_at.isoformat()
                if event.created_at
                else None
            )
        }
        for _, event in evidence
    ]