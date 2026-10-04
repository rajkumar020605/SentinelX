from datetime import datetime

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.security_event import SecurityEvent
from app.models.user import User
from app.models.incident_event import IncidentEvent
from app.models.incident import Incident
from app.schemas.security_event import SecurityEventCreate
from app.security.jwt import get_current_user


router = APIRouter(
    prefix="/security-events",
    tags=["Security Events"]
)


# =========================================================
# CREATE SECURITY EVENT
# =========================================================

@router.post("/")
def create_security_event(
    event_data: SecurityEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_event = SecurityEvent(
        event_type=event_data.event_type,
        source_ip=event_data.source_ip,
        ioc_type=event_data.ioc_type,
        ioc_value=event_data.ioc_value,
        username=event_data.username,
        action=event_data.action,
        status=event_data.status,
        severity=event_data.severity,
        message=event_data.message
    )

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    detection_result = None

    if new_event.source_ip or new_event.ioc_value:

        from app.detection.engine import run_detection

        detection_result = run_detection(
            db=db,
            source_ip=new_event.source_ip,
            username=new_event.username,
            ioc_type=new_event.ioc_type,
            ioc_value=new_event.ioc_value,
            event_id=new_event.id
        )

    return {
        "message": "Security event recorded successfully",
        "event_id": new_event.id,
        "event_type": new_event.event_type,
        "severity": new_event.severity,
        "created_by": current_user.username,
        "detection": detection_result
    }


# =========================================================
# GET SINGLE SECURITY EVENT
# =========================================================

@router.get("/{event_id}")
def get_security_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get one security event by ID.

    Used by:
    - Incident Details
    - Security investigation
    - Incident/Event correlation
    """

    event = (
        db.query(SecurityEvent)
        .filter(
            SecurityEvent.id == event_id
        )
        .first()
    )

    if not event:

        raise HTTPException(
            status_code=404,
            detail="Security event not found"
        )


    # -----------------------------------------------------
    # FIND RELATED INCIDENTS
    # -----------------------------------------------------

    incident_links = (
        db.query(IncidentEvent)
        .filter(
            IncidentEvent.event_id == event.id
        )
        .all()
    )

    incident_ids = [
        link.incident_id
        for link in incident_links
    ]

    incidents = []

    if incident_ids:

        incidents = (
            db.query(Incident)
            .filter(
                Incident.id.in_(incident_ids)
            )
            .all()
        )


    # -----------------------------------------------------
    # RETURN EVENT DETAILS
    # -----------------------------------------------------

    return {
        "id": event.id,
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
        ),

        "related_incidents": [
            {
                "incident_id": incident.id,
                "title": incident.title,
                "severity": incident.severity,
                "risk_score": incident.risk_score,
                "status": incident.status
            }
            for incident in incidents
        ]
    }


# =========================================================
# SEARCH / INVESTIGATE SECURITY EVENTS
# =========================================================

@router.get("/")
def get_security_events(
    source_ip: str | None = Query(
        default=None,
        description="Filter by source IP"
    ),

    ioc_type: str | None = Query(
        default=None,
        description="Filter by IOC type: ip, domain, url, hash"
    ),

    ioc_value: str | None = Query(
        default=None,
        description="Filter by IOC value"
    ),

    username: str | None = Query(
        default=None,
        description="Filter by username"
    ),

    event_type: str | None = Query(
        default=None,
        description="Filter by event type"
    ),

    severity: str | None = Query(
        default=None,
        description="Filter by severity"
    ),

    status: str | None = Query(
        default=None,
        description="Filter by event status"
    ),

    search: str | None = Query(
        default=None,
        description="Search IP, IOC, username or message"
    ),

    start_time: datetime | None = Query(
        default=None,
        description="Return events after this time"
    ),

    end_time: datetime | None = Query(
        default=None,
        description="Return events before this time"
    ),

    page: int = Query(
        default=1,
        ge=1
    ),

    page_size: int = Query(
        default=20,
        ge=1,
        le=100
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):
    query = db.query(SecurityEvent)


    # -----------------------------------------------------
    # EXACT FILTERS
    # -----------------------------------------------------

    if source_ip:

        query = query.filter(
            SecurityEvent.source_ip == source_ip
        )


    if ioc_type:

        query = query.filter(
            SecurityEvent.ioc_type == ioc_type
        )


    if ioc_value:

        query = query.filter(
            SecurityEvent.ioc_value == ioc_value
        )


    if username:

        query = query.filter(
            SecurityEvent.username == username
        )


    if event_type:

        query = query.filter(
            SecurityEvent.event_type == event_type
        )


    if severity:

        query = query.filter(
            SecurityEvent.severity == severity
        )


    if status:

        query = query.filter(
            SecurityEvent.status == status
        )


    # -----------------------------------------------------
    # GENERAL SEARCH
    # -----------------------------------------------------

    if search:

        search_pattern = f"%{search}%"

        query = query.filter(
            (
                SecurityEvent.source_ip.ilike(
                    search_pattern
                )
            )
            |
            (
                SecurityEvent.ioc_value.ilike(
                    search_pattern
                )
            )
            |
            (
                SecurityEvent.username.ilike(
                    search_pattern
                )
            )
            |
            (
                SecurityEvent.message.ilike(
                    search_pattern
                )
            )
        )


    # -----------------------------------------------------
    # TIME FILTERS
    # -----------------------------------------------------

    if start_time:

        query = query.filter(
            SecurityEvent.created_at >= start_time
        )


    if end_time:

        query = query.filter(
            SecurityEvent.created_at <= end_time
        )


    # -----------------------------------------------------
    # TOTAL COUNT
    # -----------------------------------------------------

    total = query.count()


    # -----------------------------------------------------
    # PAGINATION
    # -----------------------------------------------------

    offset = (
        page - 1
    ) * page_size


    events = (
        query
        .order_by(
            SecurityEvent.created_at.desc()
        )
        .offset(offset)
        .limit(page_size)
        .all()
    )


    results = []


    # -----------------------------------------------------
    # BUILD INVESTIGATION RESULTS
    # -----------------------------------------------------

    for event in events:

        incident_links = (
            db.query(IncidentEvent)
            .filter(
                IncidentEvent.event_id == event.id
            )
            .all()
        )


        incident_ids = [
            link.incident_id
            for link in incident_links
        ]


        incidents = []


        if incident_ids:

            incidents = (
                db.query(Incident)
                .filter(
                    Incident.id.in_(incident_ids)
                )
                .all()
            )


        results.append(
            {
                "event_id": event.id,

                "event_type":
                    event.event_type,

                "source_ip":
                    event.source_ip,

                "ioc_type":
                    event.ioc_type,

                "ioc_value":
                    event.ioc_value,

                "username":
                    event.username,

                "action":
                    event.action,

                "status":
                    event.status,

                "severity":
                    event.severity,

                "message":
                    event.message,

                "created_at": (
                    event.created_at.isoformat()
                    if event.created_at
                    else None
                ),

                "related_incidents": [
                    {
                        "incident_id":
                            incident.id,

                        "title":
                            incident.title,

                        "severity":
                            incident.severity,

                        "risk_score":
                            incident.risk_score,

                        "status":
                            incident.status
                    }

                    for incident in incidents
                ]
            }
        )


    # -----------------------------------------------------
    # TOTAL PAGES
    # -----------------------------------------------------

    total_pages = (
        (
            total +
            page_size -
            1
        )
        // page_size

        if total > 0

        else 0
    )


    return {
        "total_results":
            total,

        "page":
            page,

        "page_size":
            page_size,

        "total_pages":
            total_pages,

        "results":
            results
    }