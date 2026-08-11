import uuid

from fastapi import HTTPException, status
from sqlmodel import select

from app.db.session import SessionDep
from app.features.documents.models import (
    Document,
    DocumentChunk,
    DocumentStatus,
)
from app.features.documents.schemas import UploadDocumentRequest
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.features.ai.chat.service import get_user_conversation_id_service


async def create_document(
    db: SessionDep,
    user_id: uuid.UUID,
    body: UploadDocumentRequest,
) -> Document:

    conversation_id= await get_user_conversation_id_service(session=db, user_id=user_id)
    if not conversation_id:
        raise ValueError("Failed to get conversation")
    
    document = Document(
        user_id=user_id,
        conversation_id=conversation_id,
        course_id=None,
        file_name=body.file_name,
        file_url=body.file_url,
        status=DocumentStatus.processing,
    )

    db.add(document)

    await db.commit()
    await db.refresh(document)

    return document


async def get_document_by_id(
    db: SessionDep,
    document_id: uuid.UUID,
) -> Document:

    statement = select(Document).where(
        Document.id == document_id,
    )

    result = await db.exec(statement)
    document = result.one_or_none()

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document


async def get_user_documents(
    db: SessionDep,
    user_id: uuid.UUID,
) -> list[Document]:

    statement = (
        select(Document)
        .where(
            Document.user_id == user_id,
        )
        .order_by(
            Document.created_at.desc(),
        )
    )

    result = await db.exec(statement)

    return result.all()


async def get_document_chunks(
    db: AsyncSession,
    document_id: uuid.UUID,
) -> list[DocumentChunk]:

    statement = (
        select(DocumentChunk)
        .where(
            DocumentChunk.document_id == document_id,
        )
        .order_by(
            DocumentChunk.chunk_index,
        )
    )

    result = await db.exec(statement)

    return result.all()


async def get_chunk_by_id(
    db: SessionDep,
    chunk_id: uuid.UUID,
) -> DocumentChunk:

    statement = select(DocumentChunk).where(
        DocumentChunk.id == chunk_id,
    )

    result = await db.exec(statement)
    chunk = result.one_or_none()

    if chunk is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document chunk not found",
        )

    return chunk


async def get_user_document(
    db: SessionDep,
    document_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Document:

    statement = select(Document).where(
        Document.id == document_id,
        Document.user_id == user_id,
    )

    result = await db.exec(statement)
    document = result.one_or_none()

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document


async def delete_document(
    db: SessionDep,
    document_id: uuid.UUID,
    user_id: uuid.UUID,
) -> None:

    document = await get_user_document(
        db=db,
        document_id=document_id,
        user_id=user_id,
    )

    await db.delete(document)

    await db.commit()