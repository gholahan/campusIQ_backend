import uuid
import logging
from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import engine
from app.features.ai.rag.retreival import embed_query, get_last_conversation_document, search_similar_chunks
from app.features.documents.service import get_document_by_id, get_document_by_file_name

logger = logging.getLogger(__name__)


def _parse_uuid(value: str | None) -> uuid.UUID | None:
    if value is None:
        return None
    return uuid.UUID(value) if isinstance(value, str) else value


def _format_chunks(chunks: list) -> list[dict]:
    return [
        {
            "document_id": str(chunk.document_id),
            "file_name": file_name,
            "content": chunk.text,
            "page_number": chunk.page_number,
            "chunk_index": chunk.chunk_index,
        }
        for chunk, file_name in chunks
    ]


@tool(description="Search the student's document for information relevant to the user's question.")
async def search_document(
    query: str,
    state: Annotated[dict, InjectedState],
) -> list[dict]:

    logger.info("search_document query=%r", query)
    try:
        conversation_id = _parse_uuid(state["conversation_id"])
        document_id = _parse_uuid(state.get("document_id"))

        query_embedding = await embed_query(query)

        async with AsyncSession(engine, expire_on_commit=False) as session:
            if document_id:
                document = await get_document_by_id(document_id=document_id, db=session)
            else:
                document = await get_last_conversation_document(conversation_id=conversation_id, session=session)

            if document is None:
                return [{"error": "No document found for this conversation."}]

            chunks = await search_similar_chunks(
                db=session,
                document_id=document.id,
                query_embedding=query_embedding,
                limit=5,
            )

            return _format_chunks(chunks)
    except Exception:
        logger.exception("search_document failed query=%r", query)
        return [{"error": "Document retrieval failed. Do not guess the answer."}]


@tool(description="Find a document by file name and search it for information relevant to the user's question.")
async def search_document_by_name(
    file_name: str,
    query: str,
    state: Annotated[dict, InjectedState],
) -> list[dict]:

    logger.info("search_document_by_name file_name=%r query=%r", file_name, query)
    try:
        conversation_id = _parse_uuid(state["conversation_id"])
        query_embedding = await embed_query(query)

        async with AsyncSession(engine, expire_on_commit=False) as session:
            document = await get_document_by_file_name(
                db=session,
                conversation_id=conversation_id,
                file_name=file_name,
            )

            if document is None:
                return [{"error": f"No document matching '{file_name}' found for this conversation."}]

            chunks = await search_similar_chunks(
                db=session,
                document_id=document.id,
                query_embedding=query_embedding,
                limit=5,
            )

            return _format_chunks(chunks)
    except Exception:
        logger.exception("search_document_by_name failed file_name=%r", file_name)
        return [{"error": "Document retrieval failed. Do not guess the answer."}]


tools = [search_document, search_document_by_name]
