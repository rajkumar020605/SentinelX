from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.threat_intelligence import ThreatIntelligence
from app.models.user import User
from app.schemas.threat_intelligence import ThreatIntelligenceCreate
from app.security.jwt import get_current_user


router = APIRouter(
    prefix="/threat-intelligence",
    tags=["Threat Intelligence"]
)


@router.post("/")
def create_threat_intelligence(
    ioc_data: ThreatIntelligenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_ioc = (
        db.query(ThreatIntelligence)
        .filter(
            ThreatIntelligence.ioc_type == ioc_data.ioc_type,
            ThreatIntelligence.ioc_value == ioc_data.ioc_value
        )
        .first()
    )

    if existing_ioc:
        raise HTTPException(
            status_code=409,
            detail="IOC already exists"
        )
    new_ioc = ThreatIntelligence(
        ioc_type=ioc_data.ioc_type,
        ioc_value=ioc_data.ioc_value,
        threat_level=ioc_data.threat_level,
        source=ioc_data.source,
        description=ioc_data.description
    )

    db.add(new_ioc)
    db.commit()
    db.refresh(new_ioc)

    return {
        "message": "Threat intelligence added successfully",
        "ioc_id": new_ioc.id,
        "ioc_type": new_ioc.ioc_type,
        "ioc_value": new_ioc.ioc_value,
        "threat_level": new_ioc.threat_level,
        "created_by": current_user.username
    }


@router.get("/")
def get_threat_intelligence(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    iocs = (
        db.query(ThreatIntelligence)
        .order_by(ThreatIntelligence.created_at.desc())
        .all()
    )

    return [
        {
            "id": ioc.id,
            "ioc_type": ioc.ioc_type,
            "ioc_value": ioc.ioc_value,
            "threat_level": ioc.threat_level,
            "source": ioc.source,
            "description": ioc.description,
            "created_at": (
                ioc.created_at.isoformat()
                if ioc.created_at else None
            )
        }
        for ioc in iocs
    ]