from pydantic import BaseModel, Field

from campushub.models.event import EventCandidate, EventCreate

class ClassificationResult(BaseModel):
    events: list[EventCreate] = Field(default_factory=list)
    candidate_count: int
    correlated_count: int
    processing_time_ms: float | None = None
