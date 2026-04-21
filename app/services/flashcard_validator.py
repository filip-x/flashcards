"""
Validates raw JSON output from the OpenAI flashcard generation prompt.
"""
from dataclasses import dataclass


MAX_QUESTION_LEN = 500
MAX_ANSWER_LEN = 1000


@dataclass
class FlashcardData:
    question: str
    answer: str


class FlashcardValidationError(ValueError):
    pass


def validate_flashcards_json(raw: dict) -> list[FlashcardData]:
    """
    Validate the parsed JSON dict from OpenAI and return a list of
    FlashcardData objects.  Raises FlashcardValidationError on any
    structural or content issue.
    """
    if not isinstance(raw, dict):
        raise FlashcardValidationError("Expected a JSON object at the top level.")

    flashcards_raw = raw.get("flashcards")
    if flashcards_raw is None:
        raise FlashcardValidationError("Missing required key 'flashcards' in response.")
    if not isinstance(flashcards_raw, list):
        raise FlashcardValidationError("'flashcards' must be a JSON array.")
    if len(flashcards_raw) == 0:
        raise FlashcardValidationError("'flashcards' array is empty.")

    validated: list[FlashcardData] = []
    seen: set[str] = set()

    for idx, item in enumerate(flashcards_raw):
        prefix = f"flashcards[{idx}]"

        if not isinstance(item, dict):
            raise FlashcardValidationError(f"{prefix} must be an object, got {type(item).__name__}.")

        question = item.get("question")
        answer = item.get("answer")

        if not isinstance(question, str) or not question.strip():
            raise FlashcardValidationError(f"{prefix}.question must be a non-empty string.")
        if not isinstance(answer, str) or not answer.strip():
            raise FlashcardValidationError(f"{prefix}.answer must be a non-empty string.")

        question = question.strip()
        answer = answer.strip()

        if len(question) > MAX_QUESTION_LEN:
            raise FlashcardValidationError(
                f"{prefix}.question exceeds {MAX_QUESTION_LEN} characters."
            )
        if len(answer) > MAX_ANSWER_LEN:
            raise FlashcardValidationError(
                f"{prefix}.answer exceeds {MAX_ANSWER_LEN} characters."
            )

        # Deduplicate by question (case-insensitive)
        key = question.lower()
        if key in seen:
            continue
        seen.add(key)

        validated.append(FlashcardData(question=question, answer=answer))

    if not validated:
        raise FlashcardValidationError("No valid flashcards found after validation.")

    return validated
