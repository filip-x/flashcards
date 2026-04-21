from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    file_type: str
    status: Literal["uploaded", "processing", "done", "error"]
    created_at: datetime


class DocumentDetailResponse(DocumentResponse):
    raw_text: str
