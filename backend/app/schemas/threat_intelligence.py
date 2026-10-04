from ipaddress import ip_address
from typing import Literal
from urllib.parse import urlparse
import re

from pydantic import BaseModel, Field, field_validator


class ThreatIntelligenceCreate(BaseModel):

    ioc_type: Literal[
        "ip",
        "domain",
        "url",
        "hash"
    ]

    ioc_value: str = Field(
        min_length=1,
        max_length=500
    )

    threat_level: Literal[
        "low",
        "medium",
        "high",
        "critical"
    ] = "medium"

    source: str | None = None

    description: str | None = None

    @field_validator("ioc_value")
    @classmethod
    def validate_ioc_value(cls, value, info):

        ioc_type = info.data.get("ioc_type")

        # Validate IP address
        if ioc_type == "ip":
            try:
                ip_address(value)
            except ValueError:
                raise ValueError("Invalid IP address")

        # Validate domain
        elif ioc_type == "domain":
            domain_pattern = (
                r"^(?=.{1,253}$)"
                r"(?:[a-zA-Z0-9]"
                r"(?:[a-zA-Z0-9-]{0,61}"
                r"[a-zA-Z0-9])?\.)+"
                r"[a-zA-Z]{2,}$"
            )

            if not re.match(domain_pattern, value):
                raise ValueError("Invalid domain")

        # Validate URL
        elif ioc_type == "url":
            parsed = urlparse(value)

            if (
                parsed.scheme not in ["http", "https"]
                or not parsed.netloc
            ):
                raise ValueError("Invalid URL")

        # Validate MD5, SHA1 or SHA256
        elif ioc_type == "hash":
            if not re.fullmatch(
                r"[a-fA-F0-9]{32}|"
                r"[a-fA-F0-9]{40}|"
                r"[a-fA-F0-9]{64}",
                value
            ):
                raise ValueError(
                    "Invalid hash. Expected MD5, SHA1 or SHA256"
                )

        return value