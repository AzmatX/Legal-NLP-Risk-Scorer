"""
Vector Store Service for Semantic Search & Retrieval.
Uses ChromaDB with Sentence-Transformers embeddings.
"""

import logging

logger = logging.getLogger(__name__)

try:
    import uuid

    import chromadb
    from sentence_transformers import SentenceTransformer

    HAS_VECTOR_DEPS = True
except ImportError:
    HAS_VECTOR_DEPS = False
    logger.warning("Vector dependencies missing. Install: sentence-transformers chromadb")


class VectorStore:
    """Semantic search over contract clauses using embeddings."""

    def __init__(
        self, model_name: str = "all-MiniLM-L6-v2", collection_name: str = "contract_clauses"
    ):
        self.model_name = model_name
        self.collection_name = collection_name
        self.model = None
        self.client = None
        self.collection = None

        if HAS_VECTOR_DEPS:
            self._initialize()

    def _initialize(self):
        """Lazy load model and Chroma client."""
        if self.model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)

        if self.client is None:
            self.client = chromadb.Client()
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name, metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Vector store initialized: {self.collection_name}")

    def add_documents(self, texts: list[str], metadatas: list[dict] | None = None) -> list[str]:
        """Add documents to the vector store."""
        if not HAS_VECTOR_DEPS:
            logger.warning("Vector deps missing, skipping add.")
            return []

        self._initialize()

        if not texts:
            return []

        if metadatas is None:
            metadatas = [{}] * len(texts)

        # Generate embeddings
        embeddings = self.model.encode(texts, convert_to_tensor=False).tolist()

        # Generate unique IDs
        ids = [str(uuid.uuid4()) for _ in texts]

        try:
            self.collection.add(
                embeddings=embeddings, documents=texts, metadatas=metadatas, ids=ids
            )
            logger.info(f"Added {len(texts)} documents to vector store.")
            return ids
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return []

    def semantic_search(self, query: str, top_k: int = 5) -> list[dict]:
        """Search for semantically similar clauses."""
        if not HAS_VECTOR_DEPS or self.model is None:
            return [{"document": "Vector search unavailable. Install dependencies.", "distance": 0}]

        self._initialize()

        if not self.collection or self.collection.count() == 0:
            return [{"document": "No documents indexed yet.", "distance": 0}]

        try:
            query_embedding = self.model.encode([query], convert_to_tensor=False).tolist()
            results = self.collection.query(query_embeddings=query_embedding, n_results=top_k)

            documents = results.get("documents", [[]])[0]
            distances = results.get("distances", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            ids = results.get("ids", [[]])[0]

            return [
                {"document": doc, "distance": dist, "metadata": meta, "id": id_}
                for doc, dist, meta, id_ in zip(documents, distances, metadatas, ids)
            ]

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []


# ---------- Global Singleton ----------
_default_store = None


def get_vector_store() -> VectorStore:
    global _default_store
    if _default_store is None:
        _default_store = VectorStore()
    return _default_store


def semantic_search(query: str, top_k: int = 5) -> list[dict]:
    """Convenience function for semantic search."""
    store = get_vector_store()
    return store.semantic_search(query, top_k)


def index_clauses(clauses: list[str], metadatas: list[dict] | None = None) -> list[str]:
    """Convenience function to index clauses."""
    store = get_vector_store()
    return store.add_documents(clauses, metadatas)
