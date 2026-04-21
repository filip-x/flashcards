"""
OpenAI service — generates flashcards from text chunks using structured JSON output.
Features adaptive retry for rate limiting and transient API errors.
"""
import json
import logging
import asyncio
from typing import Optional

import openai
from openai import AsyncOpenAI

from app.config import get_settings
from app.services.flashcard_validator import FlashcardData, FlashcardValidationError, validate_flashcards_json
from app.services.text_chunker import chunk_text

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMRateLimitError(Exception):
    """Custom exception raised when AI rate limits are exceeded after retries."""
    pass


SYSTEM_PROMPT = """You are an expert educational content creator specializing in active recall flashcards.
Your task is to generate high-quality, comprehensive flashcards from the provided text.

Rules:
- Each flashcard must have a clear, specific QUESTION and a detailed, well-structured ANSWER.
- Questions should test deep understanding — prefer "Why", "How", "What happens when", "What is the difference between" over trivial "What is" questions.

ANSWER FORMATTING (CRITICAL):
- Use **Markdown formatting** inside the answer strings to make them readable and structured.
- Structure your answers with:
  * **Bold** for key terms and concepts.
  * Bullet points (`-`) or numbered lists for multiple points.
  * Fenced code blocks with language tags (e.g. ```bash, ```python) for any commands, code, or config.
  * Short paragraph breaks (use `\\n\\n`) to separate ideas.
- Answers should be 2-3 short paragraphs or a mix of explanation + code/example.
- If the source text contains CLI commands, scripts, config files, or API calls — you MUST reproduce them exactly in fenced code blocks.
- Include "why it works" reasoning, not just "what it is".

EXAMPLES ARE MANDATORY:
- Whenever possible, include a **practical example** in the answer that demonstrates the concept.
- For commands: show the command AND its expected output or effect.
- For concepts: give a real-world analogy or concrete scenario where it applies.
- For comparisons: show a side-by-side example of both approaches.
- Label examples clearly with a heading like **Example:** or **For instance:** so they stand out.

- Do NOT include flashcards that are too vague, trivial, or duplicative.
- Respond ONLY with valid JSON in the exact format below — no markdown wrapper, no extra text outside the JSON.

JSON format:
{
  "flashcards": [
    {"question": "...", "answer": "..."},
    {"question": "...", "answer": "..."}
  ]
}"""


def _build_user_prompt(chunk: str, num_cards: int, language: Optional[str]) -> str:
    lang_instruction = (
        f"\nIMPORTANT: Generate all flashcards in {language}."
        if language
        else ""
    )
    return (
        f"Generate exactly {num_cards} flashcards from the following text.{lang_instruction}\n\n"
        f"TEXT:\n{chunk}"
    )


async def _call_llm_with_retry(
    client: AsyncOpenAI, 
    messages: list, 
    max_retries: int = 3, 
    base_delay: float = 2.0
):
    """
    Executes an LLM call with exponential backoff for rate limits and connection errors.
    """
    for attempt in range(max_retries + 1):
        try:
            return await client.chat.completions.create(
                model=settings.groq_model,
                response_format={"type": "json_object"},
                messages=messages,
                temperature=0.4,
                max_tokens=4096,
            )
        except openai.RateLimitError as exc:
            if attempt == max_retries:
                logger.error("Rate limit exceeded after %d retries.", max_retries)
                raise LLMRateLimitError("AI provider rate limit reached. Please try again in a few minutes.") from exc
            
            delay = base_delay * (2 ** attempt)
            logger.warning("Rate limit hit. Retrying in %.1fs (Attempt %d/%d)...", delay, attempt + 1, max_retries)
            await asyncio.sleep(delay)
            
        except openai.APIConnectionError as exc:
            if attempt == max_retries:
                logger.error("Connection failed after %d retries.", max_retries)
                raise
            
            delay = base_delay * (2 ** attempt)
            logger.warning("Connection error. Retrying in %.1fs (Attempt %d/%d)...", delay, attempt + 1, max_retries)
            await asyncio.sleep(delay)
        
        except Exception as exc:
            logger.error("Unexpected LLM error: %s", exc)
            raise


async def generate_flashcards_from_text(
    text: str,
    num_cards: int = 10,
    language: Optional[str] = None,
) -> list[FlashcardData]:
    """
    Split *text* into chunks, call OpenAI for each chunk with retry logic, 
    validate and deduplicate the results.
    """
    client = AsyncOpenAI(
        api_key=settings.groq_api_key,
        base_url=settings.groq_base_url,
    )

    chunks = chunk_text(
        text,
        chunk_size=settings.max_chunk_size,
        overlap=settings.max_chunk_overlap,
    )
    if not chunks:
        return []

    # Distribute cards evenly across chunks (at least 1 per chunk)
    cards_per_chunk = max(1, num_cards // len(chunks))

    all_cards: list[FlashcardData] = []
    seen_questions: set[str] = set()

    for i, chunk in enumerate(chunks):
        # Request slightly more on the last chunk to hit the target
        request_count = cards_per_chunk if i < len(chunks) - 1 else max(
            1, num_cards - len(all_cards)
        )
        try:
            response = await _call_llm_with_retry(
                client=client,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": _build_user_prompt(chunk, request_count, language)},
                ]
            )

            raw_content = response.choices[0].message.content or "{}"
            raw_json = json.loads(raw_content)
            cards = validate_flashcards_json(raw_json)

            for card in cards:
                key = card.question.lower()
                if key not in seen_questions:
                    seen_questions.add(key)
                    all_cards.append(card)

        except FlashcardValidationError as exc:
            logger.warning("Chunk %d validation failed: %s", i, exc)
        except LLMRateLimitError:
            # Re-raise so the router can handle the 429
            raise
        except Exception as exc:
            logger.error("OpenAI call failed for chunk %d after retries: %s", i, exc)
            raise

        if len(all_cards) >= num_cards:
            break

    return all_cards[:num_cards]
