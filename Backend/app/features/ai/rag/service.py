import uuid
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.common.enums import DocumentStatus
from app.features.documents.models import Document, DocumentChunk
from app.features.ai.rag.schemas import EmbeddedChunk


async def save_chunks(
    session: AsyncSession,
    document_id: uuid.UUID,
    embedded_chunks: list[EmbeddedChunk],
    page_count: int,
) -> None:

    for index, chunk in enumerate(embedded_chunks):

        session.add(
            DocumentChunk(
                document_id=document_id,
                text=chunk.content,
                embedding=chunk.embedding,
                page_number=chunk.metadata.page,
                chunk_index=index,
            )
        )

    result = await session.exec(
        select(Document).where(
            Document.id == document_id
        )
    )

    document = result.first()

    if document:
        document.status = DocumentStatus.ready
        document.page_count = page_count

    await session.commit()


async def mark_document_failed(
    session: AsyncSession,
    document_id: uuid.UUID,
) -> None:

    result = await session.exec(
        select(Document).where(
            Document.id == document_id
        )
    )

    document = result.first()

    if document:
        document.status = DocumentStatus.failed

    await session.commit()
