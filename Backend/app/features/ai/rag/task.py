import asyncio
import logging
import uuid

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

import app.db.base  # noqa: F401
from app.core.celery import celery_app
from app.core.config import DATABASE_URL
from app.features.ai.rag.ingestion import process_pdf


logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="upload.task",
)
def upload_document(
    self,
    document_id: str,
    file_url: str,
) -> None:

    try:
        asyncio.run(
            run_process_pdf(
                document_id=document_id,
                file_url=file_url,
            )
        )

    except Exception:
        logger.exception(
            "[%s] Celery task failed",
            document_id,
        )
        raise


async def run_process_pdf(
    document_id: str,
    file_url: str,
) -> None:

    logger.info(
        "[%s] Creating database engine",
        document_id,
    )

    engine = create_async_engine(
        DATABASE_URL,
        connect_args={
            "statement_cache_size": 0,
        },
    )

    try:
        async with AsyncSession(
            engine,
            expire_on_commit=False,
        ) as session:

            await process_pdf(
                file_url=file_url,
                document_id=uuid.UUID(document_id),
                session=session,
            )

    finally:
        await engine.dispose()