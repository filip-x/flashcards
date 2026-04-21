"""
Reviews router — SM-2 spaced repetition review loop.
"""
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.flashcard import Flashcard
from app.models.review import Review
from app.schemas.review import ReviewHistoryItem, ReviewRequest, ReviewResponse
from app.services.sm2 import sm2_update

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post(
    "/",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a review for a flashcard (SM-2 update)",
)
async def submit_review(
    request: ReviewRequest,
    db: AsyncSession = Depends(get_db),
) -> ReviewResponse:
    """
    Submit a quality score (0–5) for a flashcard.  The SM-2 algorithm
    updates the card's ease factor, interval, and next due date.
    """
    result = await db.execute(select(Flashcard).where(Flashcard.id == request.flashcard_id))
    flashcard = result.scalar_one_or_none()
    if not flashcard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flashcard not found.")

    sm2 = sm2_update(
        ease_factor=flashcard.ease_factor,
        interval=flashcard.interval,
        repetitions=flashcard.repetitions,
        quality=request.quality,
    )

    # Persist updated SM-2 state on the flashcard
    flashcard.ease_factor = sm2.ease_factor
    flashcard.interval = sm2.interval
    flashcard.repetitions = sm2.repetitions
    flashcard.due_date = sm2.due_date
    flashcard.updated_at = datetime.now(timezone.utc)

    # Log the review
    review = Review(
        flashcard_id=flashcard.id,
        quality=request.quality,
        scheduled_days=sm2.interval,
    )
    db.add(review)
    await db.commit()  # Explicitly commit after each review to ensure persistence
    await db.refresh(review)

    logger.info(
        "Review for flashcard %s: quality=%d, next interval=%d days, due=%s",
        flashcard.id,
        request.quality,
        sm2.interval,
        sm2.due_date,
    )

    return ReviewResponse(
        id=review.id,
        flashcard_id=review.flashcard_id,
        quality=review.quality,
        scheduled_days=review.scheduled_days,
        reviewed_at=review.reviewed_at,
        next_due_date=sm2.due_date,
    )


@router.get(
    "/{flashcard_id}",
    response_model=list[ReviewHistoryItem],
    summary="Get review history for a flashcard",
)
async def get_review_history(
    flashcard_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[ReviewHistoryItem]:
    # Verify flashcard exists
    fc_result = await db.execute(select(Flashcard).where(Flashcard.id == flashcard_id))
    if not fc_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flashcard not found.")

    result = await db.execute(
        select(Review)
        .where(Review.flashcard_id == flashcard_id)
        .order_by(Review.reviewed_at.asc())
    )
    reviews = result.scalars().all()
    return [ReviewHistoryItem.model_validate(r) for r in reviews]
