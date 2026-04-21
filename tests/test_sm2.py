"""
SM-2 algorithm unit tests.
"""
import pytest
from datetime import date, timedelta
from datetime import datetime, timezone

from app.services.sm2 import sm2_update, SM2Result, MIN_EASE_FACTOR


class TestSM2Update:
    """Test suite for the SM-2 spaced repetition algorithm."""

    DEFAULT_EF = 2.5
    DEFAULT_INTERVAL = 1
    DEFAULT_REPS = 0

    def test_first_successful_review_quality_3(self):
        result = sm2_update(self.DEFAULT_EF, self.DEFAULT_INTERVAL, self.DEFAULT_REPS, quality=3)
        assert result.repetitions == 1
        assert result.interval == 1
        assert result.ease_factor >= MIN_EASE_FACTOR

    def test_second_successful_review_gives_interval_6(self):
        r1 = sm2_update(self.DEFAULT_EF, 1, 1, quality=4)
        assert r1.interval == 6
        assert r1.repetitions == 2

    def test_third_review_uses_ef_multiplier(self):
        r = sm2_update(2.5, 6, 2, quality=4)
        assert r.interval == round(6 * 2.5)
        assert r.repetitions == 3

    def test_perfect_quality_increases_ef(self):
        result = sm2_update(2.5, 6, 2, quality=5)
        assert result.ease_factor > 2.5

    def test_poor_quality_decreases_ef(self):
        result = sm2_update(2.5, 6, 2, quality=3)
        assert result.ease_factor < 2.5

    def test_ef_never_drops_below_minimum(self):
        # Apply many low-quality reviews
        ef, interval, reps = 2.5, 1, 0
        for _ in range(10):
            r = sm2_update(ef, interval, reps, quality=3)
            ef, interval, reps = r.ease_factor, r.interval, r.repetitions
        assert ef >= MIN_EASE_FACTOR

    def test_failed_review_resets_repetitions(self):
        result = sm2_update(2.5, 10, 5, quality=2)
        assert result.repetitions == 0
        assert result.interval == 1

    def test_failed_review_does_not_change_ef(self):
        result = sm2_update(2.5, 10, 5, quality=1)
        assert result.ease_factor == 2.5
        assert result.repetitions == 0

    def test_complete_blackout_resets_sequence(self):
        result = sm2_update(2.5, 20, 8, quality=0)
        assert result.repetitions == 0
        assert result.interval == 1

    def test_due_date_is_today_plus_interval(self):
        result = sm2_update(2.5, 1, 0, quality=4)
        expected = datetime.now(timezone.utc).date() + timedelta(days=result.interval)
        assert result.due_date == expected

    def test_invalid_quality_raises_value_error(self):
        with pytest.raises(ValueError, match="quality must be 0–5"):
            sm2_update(2.5, 1, 0, quality=6)

    def test_returns_frozen_dataclass(self):
        result = sm2_update(2.5, 1, 0, quality=4)
        assert isinstance(result, SM2Result)
        with pytest.raises(Exception):
            result.interval = 999  # frozen

    def test_quality_4_successful_progression(self):
        ef, interval, reps = 2.5, 1, 0
        for expected_reps in range(1, 6):
            r = sm2_update(ef, interval, reps, quality=4)
            ef, interval, reps = r.ease_factor, r.interval, r.repetitions
            assert r.repetitions == expected_reps
