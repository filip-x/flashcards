"""
SM-2 spaced repetition algorithm implementation.

Reference: https://www.supermemo.com/en/archives1990-2015/english/ol/sm2

Quality scale (0–5):
  0 — Complete blackout
  1 — Incorrect; correct answer seemed easy to recall
  2 — Incorrect; correct answer remembered upon seeing it
  3 — Correct with serious difficulty
  4 — Correct with some hesitation
  5 — Perfect response
"""
from dataclasses import dataclass
from datetime import date, timedelta
from datetime import datetime, timezone


MIN_EASE_FACTOR = 1.3


@dataclass(frozen=True)
class SM2Result:
    ease_factor: float
    interval: int       # days until next review
    repetitions: int
    due_date: date


def sm2_update(
    ease_factor: float,
    interval: int,
    repetitions: int,
    quality: int,
) -> SM2Result:
    """
    Compute updated SM-2 values after one review session.

    Args:
        ease_factor: Current ease factor (≥ 1.3).
        interval: Current interval in days.
        repetitions: Number of successful repetitions so far.
        quality: Review quality score (0–5).

    Returns:
        SM2Result with updated values and the next due date.
    """
    if not (0 <= quality <= 5):
        raise ValueError(f"quality must be 0–5, got {quality}")

    if quality < 3:
        # Failed recall — reset repetition sequence
        new_repetitions = 0
        new_interval = 1
        new_ease_factor = ease_factor  # EF does not change on failure
    else:
        # Successful recall
        new_repetitions = repetitions + 1
        if new_repetitions == 1:
            new_interval = 1
        elif new_repetitions == 2:
            new_interval = 6
        else:
            new_interval = round(interval * ease_factor)

        # Update ease factor based on quality
        new_ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_ease_factor = max(MIN_EASE_FACTOR, new_ease_factor)

    today = datetime.now(timezone.utc).date()
    due_date = today + timedelta(days=new_interval)

    return SM2Result(
        ease_factor=round(new_ease_factor, 4),
        interval=new_interval,
        repetitions=new_repetitions,
        due_date=due_date,
    )
