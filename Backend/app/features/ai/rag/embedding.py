from langchain_voyageai import VoyageAIEmbeddings
from app.core.config import VOYAGEAI_EMBEDDER_KEY
from app.features.ai.rag.schemas import (
    TextChunk,
    EmbeddedChunk,
)

if VOYAGEAI_EMBEDDER_KEY is None:
    raise ValueError(
        "VOYAGEAI_EMBEDDER_KEY is not set in the environment variables."
    )

embedder = VoyageAIEmbeddings(
    api_key=VOYAGEAI_EMBEDDER_KEY, # type: ignore
    model="voyage-4",
)


async def generate_embeddings(
    chunks: list[TextChunk],
) -> list[EmbeddedChunk]:

    texts = [
        chunk.content
        for chunk in chunks
    ]

    vectors = await embedder.aembed_documents(
        texts
    )
    print(len(vectors[0]))
    embedded_chunks: list[EmbeddedChunk] = []

    for chunk, vector in zip(
        chunks,
        vectors,
    ):

        embedded_chunks.append(
            EmbeddedChunk(
                content=chunk.content,
                embedding=vector,
                metadata=chunk.metadata,
            )
        )

    return embedded_chunks