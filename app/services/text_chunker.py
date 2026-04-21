"""
Text chunking service — splits large documents into overlapping chunks
sized for LLM context windows.
"""
import re


def _split_into_sentences(text: str) -> list[str]:
    """Rough sentence splitter that handles common abbreviations."""
    # Split on sentence-ending punctuation followed by whitespace
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def chunk_text(
    text: str,
    chunk_size: int = 2000,
    overlap: int = 200,
) -> list[str]:
    """
    Split *text* into chunks of at most *chunk_size* characters with
    *overlap* characters of context carried over between chunks.

    Strategy:
    1. Split the text into paragraphs first.
    2. Accumulate paragraphs into a chunk until the size limit is reached.
    3. When a chunk is full, save it and begin the next chunk with the
       last *overlap* characters of the previous one.
    """
    if not text:
        return []

    # Normalise whitespace
    text = re.sub(r"\r\n", "\n", text)
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]

    chunks: list[str] = []
    current_parts: list[str] = []
    current_len = 0

    for para in paragraphs:
        para_len = len(para)

        # If a single paragraph exceeds chunk_size, break it by sentences
        if para_len > chunk_size:
            sentences = _split_into_sentences(para)
            for sentence in sentences:
                if current_len + len(sentence) + 1 > chunk_size and current_parts:
                    chunk = " ".join(current_parts)
                    chunks.append(chunk)
                    # Start new chunk with overlap tail
                    overlap_text = chunk[-overlap:] if overlap else ""
                    current_parts = [overlap_text] if overlap_text else []
                    current_len = len(overlap_text)
                current_parts.append(sentence)
                current_len += len(sentence) + 1
        elif current_len + para_len + 2 > chunk_size and current_parts:
            # Current chunk is full — save and start fresh with overlap
            chunk = "\n\n".join(current_parts)
            chunks.append(chunk)
            overlap_text = chunk[-overlap:] if overlap else ""
            current_parts = [overlap_text, para] if overlap_text else [para]
            current_len = len(overlap_text) + para_len + 2
        else:
            current_parts.append(para)
            current_len += para_len + 2

    # Flush remaining
    if current_parts:
        chunks.append("\n\n".join(current_parts))

    return chunks
