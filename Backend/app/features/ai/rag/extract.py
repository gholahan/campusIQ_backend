import fitz
import httpx

from app.features.ai.rag.schemas import PDFPage


async def extract_pdf_pages(
    file_url: str,
) -> list[PDFPage]:

    async with httpx.AsyncClient() as client:
        response = await client.get(file_url)
        response.raise_for_status()

    document = fitz.open(
        stream=response.content,
        filetype="pdf",
    )

    pages: list[PDFPage] = []

    try:
        for page_number, page in enumerate(document):

            pages.append(
                PDFPage(
                    page=page_number + 1,
                    text=page.get_text(),
                )
            )

    finally:
        document.close()

    return pages