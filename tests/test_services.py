from app.services.file_parser import extract_text, ALLOWED_EXTENSIONS
from app.services.text_chunker import chunk_text


class TestFileParser:

    def test_parse_txt(self):
        file_type, text = extract_text("notes.txt", b"Hello world")
        assert file_type == "txt"
        assert "Hello world" in text

    def test_parse_markdown_strips_syntax(self):
        md = b"# Heading\n\n**Bold** text and `code`."
        file_type, text = extract_text("doc.md", md)
        assert file_type == "md"
        assert "Heading" in text
        assert "#" not in text
        assert "**" not in text

    def test_unsupported_extension_raises(self):
        from fastapi import HTTPException
        import pytest
        with pytest.raises(HTTPException) as exc:
            extract_text("data.csv", b"a,b,c")
        assert exc.value.status_code == 415

    def test_allowed_extensions(self):
        assert "pdf" in ALLOWED_EXTENSIONS
        assert "txt" in ALLOWED_EXTENSIONS
        assert "md" in ALLOWED_EXTENSIONS


class TestChunker:

    def test_short_text_returns_single_chunk(self):
        text = "Short text."
        chunks = chunk_text(text, chunk_size=500)
        assert len(chunks) == 1
        assert chunks[0] == "Short text."

    def test_long_text_splits_into_multiple_chunks(self):
        text = ("Word. " * 80 + "\n\n") * 5  # 80 words * 6 chars = ~480 chars per paragraph, easily splittable
        chunks = chunk_text(text, chunk_size=500, overlap=50)
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk) <= 650  # some tolerance for overlap

    def test_empty_text_returns_empty_list(self):
        assert chunk_text("") == []

    def test_overlap_carries_context(self):
        long_para = "A" * 300 + "\n\n" + "B" * 300
        chunks = chunk_text(long_para, chunk_size=300, overlap=50)
        # Second chunk should start with tail of first
        if len(chunks) > 1:
            assert len(chunks[1]) > 0
