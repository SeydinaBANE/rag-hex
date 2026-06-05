from rag_system.domain.model.document import Chunk, ChunkMetadata, Document
from rag_system.domain.port.inbound.ingestion_use_case import IngestionUseCase
from rag_system.domain.port.outbound.document_store_port import DocumentStorePort
from rag_system.domain.port.outbound.embedder_port import EmbedderPort
from rag_system.domain.port.outbound.retriever_port import RetrieverPort


class IngestionService(IngestionUseCase):
    def __init__(
        self,
        embedder: EmbedderPort,
        document_store: DocumentStorePort,
        retriever: RetrieverPort,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
    ) -> None:
        self._embedder = embedder
        self._document_store = document_store
        self._retriever = retriever
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    async def ingest(self, document: Document) -> None:
        chunks = self._chunk_document(document)
        texts = [c.content for c in chunks]
        embeddings = await self._embedder.embed_batch(texts)

        for chunk, embedding in zip(chunks, embeddings, strict=True):
            chunk.embedding = embedding

        document.chunks = chunks
        await self._document_store.store(document)

    def _chunk_document(self, document: Document) -> list[Chunk]:
        content = document.content
        chunks: list[Chunk] = []
        start = 0
        position = 0

        while start < len(content):
            end = min(start + self._chunk_size, len(content))
            chunk_content = content[start:end]
            chunk_id = f"{document.id}__chunk_{position}"

            chunks.append(
                Chunk(
                    id=chunk_id,
                    content=chunk_content,
                    metadata=ChunkMetadata(
                        source_document_id=document.id,
                        position=position,
                    ),
                )
            )

            position += 1
            start += self._chunk_size - self._chunk_overlap

        return chunks
