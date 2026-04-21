import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    flashcard_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("flashcards.id", ondelete="CASCADE"), nullable=False, index=True
    )
    quality: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-5
    scheduled_days: Mapped[int] = mapped_column(Integer, nullable=False)  # new interval after review
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
