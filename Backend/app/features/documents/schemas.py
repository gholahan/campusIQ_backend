import uuid
from datetime import datetime
from pydantic import BaseModel
from app.common.enums import DocumentStatus


class UploadDocumentRequest(BaseModel):
    file_name: str
    file_url: str


class DocumentResponse(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID | None = None
    file_name: str
    file_url: str
    status: DocumentStatus
    page_count: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}

class DocumentChunkResponse(BaseModel):
    id: uuid.UUID
    document_id: uuid.UUID
    text: str
    page_number: int | None
    chunk_index: int
    created_at: datetime

    model_config = {"from_attributes": True}

