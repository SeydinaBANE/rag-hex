class RagError(Exception):
    pass


class EmbeddingError(RagError):
    pass


class LLMError(RagError):
    pass


class RetrievalError(RagError):
    pass
