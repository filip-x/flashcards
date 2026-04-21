"""
Flashcard JSON validator unit tests.
"""
import pytest

from app.services.flashcard_validator import (
    FlashcardData,
    FlashcardValidationError,
    validate_flashcards_json,
)


class TestValidateFlashcardsJson:

    def _valid(self, n: int = 2) -> dict:
        return {
            "flashcards": [
                {"question": f"Question {i}?", "answer": f"Answer {i}."}
                for i in range(n)
            ]
        }

    def test_valid_input_returns_list(self):
        result = validate_flashcards_json(self._valid())
        assert len(result) == 2
        assert all(isinstance(c, FlashcardData) for c in result)

    def test_missing_flashcards_key_raises(self):
        with pytest.raises(FlashcardValidationError, match="Missing required key"):
            validate_flashcards_json({"cards": []})

    def test_flashcards_not_list_raises(self):
        with pytest.raises(FlashcardValidationError, match="must be a JSON array"):
            validate_flashcards_json({"flashcards": "oops"})

    def test_empty_flashcards_array_raises(self):
        with pytest.raises(FlashcardValidationError, match="empty"):
            validate_flashcards_json({"flashcards": []})

    def test_missing_question_raises(self):
        with pytest.raises(FlashcardValidationError, match="question"):
            validate_flashcards_json({"flashcards": [{"answer": "A"}]})

    def test_missing_answer_raises(self):
        with pytest.raises(FlashcardValidationError, match="answer"):
            validate_flashcards_json({"flashcards": [{"question": "Q?"}]})

    def test_empty_question_raises(self):
        with pytest.raises(FlashcardValidationError, match="question"):
            validate_flashcards_json({"flashcards": [{"question": "  ", "answer": "A"}]})

    def test_empty_answer_raises(self):
        with pytest.raises(FlashcardValidationError, match="answer"):
            validate_flashcards_json({"flashcards": [{"question": "Q?", "answer": ""}]})

    def test_question_too_long_raises(self):
        with pytest.raises(FlashcardValidationError, match="exceeds"):
            validate_flashcards_json(
                {"flashcards": [{"question": "Q" * 501, "answer": "A"}]}
            )

    def test_answer_too_long_raises(self):
        with pytest.raises(FlashcardValidationError, match="exceeds"):
            validate_flashcards_json(
                {"flashcards": [{"question": "Q?", "answer": "A" * 1001}]}
            )

    def test_duplicate_questions_deduplicated(self):
        raw = {
            "flashcards": [
                {"question": "Same question?", "answer": "First"},
                {"question": "same question?", "answer": "Duplicate"},  # same key lower
                {"question": "Different question?", "answer": "Other"},
            ]
        }
        result = validate_flashcards_json(raw)
        assert len(result) == 2

    def test_whitespace_stripped_from_fields(self):
        raw = {"flashcards": [{"question": "  Q?  ", "answer": "  A.  "}]}
        result = validate_flashcards_json(raw)
        assert result[0].question == "Q?"
        assert result[0].answer == "A."

    def test_non_dict_top_level_raises(self):
        with pytest.raises(FlashcardValidationError, match="JSON object"):
            validate_flashcards_json([{"question": "Q?", "answer": "A"}])  # type: ignore

    def test_non_dict_item_in_array_raises(self):
        with pytest.raises(FlashcardValidationError, match="must be an object"):
            validate_flashcards_json({"flashcards": ["not a dict"]})
