from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone

from app.database import Base


class ThreatIntelligence(Base):
    __tablename__ = "threat_intelligence"

    id = Column(Integer, primary_key=True, index=True)

    ioc_type = Column(String(30), nullable=False, index=True)

    ioc_value = Column(String(500), nullable=False, index=True)

    threat_level = Column(String(20), default="medium", nullable=False)

    source = Column(String(200), nullable=True)

    description = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )