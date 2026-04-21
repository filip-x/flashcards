"""
Documents router — file upload and document retrieval.
"""
import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import get_settings
from app.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentDetailResponse, DocumentResponse
from app.services.file_parser import extract_text

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a PDF, TXT, or Markdown file",
)
async def upload_document(
    file: UploadFile = File(..., description="PDF, TXT, or .md file to upload"),
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    """
    Upload a document. The text is extracted immediately and stored.
    Use the returned `id` to generate flashcards.
    """
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    content = await file.read()

    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds the {settings.max_file_size_mb} MB limit.",
        )
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded file is empty.",
        )

    file_type, raw_text = extract_text(file.filename or "upload", content)

    document = Document(
        filename=file.filename or "upload",
        file_type=file_type,
        raw_text=raw_text,
        status="uploaded",
    )
    db.add(document)
    await db.flush()  # get generated id without committing yet

    logger.info("Document %s uploaded (%s, %d chars)", document.id, file_type, len(raw_text))
    return DocumentResponse.model_validate(document)


@router.get(
    "/",
    response_model=list[DocumentResponse],
    summary="List all uploaded documents",
)
async def list_documents(
    db: AsyncSession = Depends(get_db),
) -> list[DocumentResponse]:
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    documents = result.scalars().all()
    return [DocumentResponse.model_validate(d) for d in documents]


@router.get(
    "/{document_id}",
    response_model=DocumentDetailResponse,
    summary="Get a document (including extracted text)",
)
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
) -> DocumentDetailResponse:
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return DocumentDetailResponse.model_validate(document)
