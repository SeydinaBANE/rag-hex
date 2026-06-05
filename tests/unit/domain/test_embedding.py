import pytest

from rag_system.domain.model.embedding import Embedding


class TestEmbedding:
    def test_create_valid_embedding(self) -> None:
        emb = Embedding(vector=[0.1, 0.2, 0.3], model="test-model", dimensions=3)
        assert emb.vector == [0.1, 0.2, 0.3]
        assert emb.model == "test-model"
        assert emb.dimensions == 3

    def test_immutable(self) -> None:
        emb = Embedding(vector=[0.1], model="test", dimensions=1)
        with pytest.raises(AttributeError):
            emb.vector = [0.2]  # type: ignore[misc]

    def test_reject_negative_dimensions(self) -> None:
        with pytest.raises(ValueError, match="dimensions must be positive"):
            Embedding(vector=[], model="test", dimensions=0)

    def test_reject_mismatched_dimensions(self) -> None:
        with pytest.raises(ValueError, match="vector length"):
            Embedding(vector=[0.1, 0.2], model="test", dimensions=3)
