from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)

from app.features.ai.rag.schemas import (
    PDFPage,
    TextChunk,
    ChunkMetadata,
)


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)


def create_chunks(
    pages: list[PDFPage],
) -> list[TextChunk]:

    chunks: list[TextChunk] = []

    for page in pages:

        cleaned_text = clean_text(
            page.text
        )

        page_chunks = text_splitter.split_text(
            cleaned_text
        )

        for chunk in page_chunks:

            chunks.append(
                TextChunk(
                    content=chunk,
                    metadata=ChunkMetadata(
                        page=page.page
                    ),
                )
            )

    return chunks

def clean_text(text: str) -> str:

    text = text.replace("\n", " ")

    text = " ".join(text.split())

    return text

