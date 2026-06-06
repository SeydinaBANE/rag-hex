# domain/port/outbound

Ports de sortie : les services externes dont le domaine a besoin.

| Fichier | Port | Méthodes |
|---|---|---|
| `embedder_port.py` | EmbedderPort | embed, embed_batch |
| `retriever_port.py` | RetrieverPort | search |
| `llm_port.py` | LLMPort | generate |
| `document_store_port.py` | DocumentStorePort | store, get, delete |
| `reranker_port.py` | RerankerPort | rerank |
