from pydantic import BaseModel


class PDFPage(BaseModel):
    page: int
    text: str


class ChunkMetadata(BaseModel):
    page: int


class TextChunk(BaseModel):
    content: str
    metadata: ChunkMetadata


class EmbeddedChunk(BaseModel):
    content: str
    embedding: list[float]
    metadata: ChunkMetadata