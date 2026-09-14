from sqlmodel import select
import uuid

from sqlmodel import select

from app.db.session import SessionDep
from app.features.documents.models import (
    Document,
    DocumentChunk,
)
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.features.ai.rag.embedding import embedder



async def embed_query(
    query: str,
) -> list[float]:

    return await embedder.aembed_query(query)



async def get_last_conversation_document(
    conversation_id: uuid.UUID, session: AsyncSession
) -> Document | None:
    statement = (
        select(Document)
        .where(Document.conversation_id == conversation_id)
        .order_by(Document.created_at.desc())
        .limit(1)
    )

    result = await session.exec(statement)
    document = result.one_or_none()

    return document



async def search_similar_chunks(
    db: SessionDep,
    document_id: uuid.UUID,
    query_embedding: list[float],
    limit: int = 5,
) -> list[tuple[DocumentChunk, str]]:

    statement = (
        select(DocumentChunk, Document.file_name)
        .join(Document, DocumentChunk.document_id == Document.id)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
        .limit(limit)
    )

    result = await db.exec(statement)

    return result.all()

