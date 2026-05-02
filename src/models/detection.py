from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class Topic(StrEnum):
    health = "health"
    finance = "finance"
    legal = "legal"
    hr = "hr"


class DetectionSettings(BaseModel):
    health: bool = False
    finance: bool = False
    legal: bool = False
    hr: bool = False


class PromptRequest(BaseModel):
    prompt: str
    settings: DetectionSettings


class DetectionResult(BaseModel):
    detected_topics: list[str]


class AuditEntry(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    endpoint: str
    prompt: str
    detected_topics: list[str]
