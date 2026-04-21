from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ReviewRequest(BaseModel):
    flashcard_id: str
    quality: int = Field(
        ge=0,
        le=5,
        description="Review quality score: 0=complete blackout, 5=perfect response.",
    )


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    flashcard_id: str
    quality: int
    scheduled_days: int
    reviewed_at: datetime
    next_due_date: date


class ReviewHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    quality: int
    scheduled_days: int
    reviewed_at: datetime
