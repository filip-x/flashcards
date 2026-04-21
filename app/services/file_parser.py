"""
File parser service — extracts plain text from PDF, TXT, and Markdown uploads.
"""
import io
import re

from fastapi import HTTPException, status


def _parse_pdf(content: bytes) -> str:
    try:
        from PyPDF2 import PdfReader

        reader = PdfReader(io.BytesIO(content))
        pages: list[str] = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text.strip())
        if not pages:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Could not extract any text from the PDF. The file may be scanned or image-based.",
            )
        return "\n\n".join(pages)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse PDF: {exc}",
        ) from exc


def _parse_txt(content: bytes) -> str:
    try:
        return content.decode("utf-8", errors="replace").strip()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to read text file: {exc}",
        ) from exc


def _parse_markdown(content: bytes) -> str:
    """Strip common Markdown syntax to produce readable plain text."""
    text = content.decode("utf-8", errors="replace")

    # Remove fenced code blocks
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`[^`]+`", "", text)

    # Remove headings markup but keep text
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)

    # Remove bold/italic
    text = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", text)
    text = re.sub(r"_{1,2}([^_]+)_{1,2}", r"\1", text)

    # Remove links — keep label
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # Remove images
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # Remove horizontal rules
    text = re.sub(r"^[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)

    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


_PARSERS = {
    "pdf": _parse_pdf,
    "txt": _parse_txt,
    "md": _parse_markdown,
    "markdown": _parse_markdown,
}

ALLOWED_EXTENSIONS = frozenset(_PARSERS.keys())


def get_file_type(filename: str) -> str:
    """Return the normalised extension (lower-case, no dot)."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type '.{ext}'. Accepted: {sorted(ALLOWED_EXTENSIONS)}",
        )
    return ext


def extract_text(filename: str, content: bytes) -> tuple[str, str]:
    """
    Parse the uploaded file and return (file_type, extracted_text).
    Raises HTTPException on unsupported type or parse failure.
    """
    file_type = get_file_type(filename)
    parser = _PARSERS[file_type]
    text = parser(content)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Extracted text is empty. Please upload a non-empty document.",
        )
    return file_type, text
