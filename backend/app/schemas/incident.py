from typing import Literal

from pydantic import BaseModel, Field


class IncidentCreate(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=200
    )

    description: str | None = None

    incident_type: str = Field(
        min_length=2,
        max_length=100
    )

    detection_rule: str | None = None

    source_ip: str | None = None

    username: str | None = None

    severity: str = "medium"

    risk_score: int = Field(
        default=0,
        ge=0,
        le=100
    )


class IncidentStatusUpdate(BaseModel):
    status: Literal[
        "open",
        "investigating",
        "resolved",
        "closed"
    ]


class InvestigationUpdate(BaseModel):
    investigation_notes: str = Field(
        min_length=1,
        max_length=5000
    )


class IncidentAssignment(BaseModel):
    assigned_to: int = Field(
        ge=1
    )