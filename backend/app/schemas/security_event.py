from pydantic import BaseModel, Field
from typing import Optional


class SecurityEventCreate(BaseModel):
    event_type: str = Field(min_length=2, max_length=50)
    source_ip: Optional[str] = None
    ioc_type: Optional[str] = None
    ioc_value: Optional[str] = None
    username: Optional[str] = None
    action: Optional[str] = None
    status: Optional[str] = None
    severity: str = "low"
    message: Optional[str] = None