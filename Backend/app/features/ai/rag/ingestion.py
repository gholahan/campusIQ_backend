import logging
import uuid

from app.features.ai.rag.extract import extract_pdf_pages
from app.features.ai.rag.chunk import create_chunks
from app.db.session import SessionDep
from app.features.ai.rag.embedding import generate_embeddings
from app.features.ai.rag.service import (
    save_chunks,
    mark_document_failed,
)


logger = logging.getLogger(__name__)


async def process_pdf(
    session: SessionDep,
    document_id: uuid.UUID,
    file_url: str,
) -> None:

    try:
        logger.info(
            "[%s] Starting PDF processing",
            document_id,
        )

        # 1. Extract PDF pages

        pages = await extract_pdf_pages(
            file_url
        )

        # 2. Chunk extracted text

        chunks = create_chunks(
            pages
        )

        # 3. Generate embeddings

        embedded_chunks = await generate_embeddings(
            chunks
        )

        # 4. Save chunks + embeddings

        await save_chunks(
            session=session,
            document_id=document_id,
            embedded_chunks=embedded_chunks,
            page_count=len(pages),
        )

        logger.info(
            "[%s] PDF processing completed successfully",
            document_id,
        )

    except Exception:
        logger.exception(
            "[%s] PDF processing failed",
            document_id,
        )
        await session.rollback()

        await mark_document_failed(
            session=session,
            document_id=document_id,
        )

        raise