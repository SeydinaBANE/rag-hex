from rag_system.domain.model.document import Chunk, ChunkMetadata, Document


class TestDocument:
    def test_create_document_without_chunks(self) -> None:
        doc = Document(id="doc-1", content="Hello world", metadata={"source": "test"})
        assert doc.id == "doc-1"
        assert doc.content == "Hello world"
        assert doc.metadata == {"source": "test"}
        assert doc.chunks is None

    def test_create_document_with_chunks(self) -> None:
        doc = Document(
            id="doc-1",
            content="Hello world",
            metadata={"source": "test"},
            chunks=[
                Chunk(
                    id="chunk-1",
                    content="Hello",
                    metadata=ChunkMetadata(source_document_id="doc-1", position=0),
                ),
                Chunk(
                    id="chunk-2",
                    content="world",
                    metadata=ChunkMetadata(source_document_id="doc-1", position=1),
                ),
            ],
        )
        assert doc.chunks is not None
        assert len(doc.chunks) == 2

    def test_create_chunk_with_page(self) -> None:
        meta = ChunkMetadata(source_document_id="doc-1", page=3, position=1)
        assert meta.page == 3

    def test_chunk_default_page_is_none(self) -> None:
        meta = ChunkMetadata(source_document_id="doc-1", position=0)
        assert meta.page is None
