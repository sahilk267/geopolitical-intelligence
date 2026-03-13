"""
RAG Service — Persona Long-Term Memory
Uses ChromaDB as a local vector database to store and recall past analyses.
This gives each persona "memory" — the ability to reference their own past work.
"""
import os
import logging
import uuid
from typing import Optional, List, Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)

# Lazy-loaded ChromaDB client
_chroma_client = None
_embed_fn = None


def _get_chroma_client():
    """Lazy-initialize ChromaDB client."""
    global _chroma_client
    if _chroma_client is None:
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings

            persist_dir = getattr(settings, "CHROMADB_DIR", "./data/chromadb")
            os.makedirs(persist_dir, exist_ok=True)

            _chroma_client = chromadb.PersistentClient(
                path=persist_dir,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            logger.info(f"ChromaDB initialized at {persist_dir}")
        except ImportError:
            logger.error("ChromaDB not installed. Run: pip install chromadb")
            raise
    return _chroma_client


def _get_collection(profile_id: str):
    """Get or create a ChromaDB collection for a specific persona."""
    client = _get_chroma_client()
    # Sanitize collection name (ChromaDB requires alphanumeric + underscores)
    safe_name = f"persona_{profile_id.replace('-', '_')[:32]}"
    return client.get_or_create_collection(
        name=safe_name,
        metadata={"hnsw:space": "cosine"},
    )


class RAGService:
    """Retrieval-Augmented Generation service for persona memory."""

    async def store_memory(
        self,
        profile_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Store a text chunk in the persona's memory.
        The text is automatically embedded by ChromaDB's default embedding function.
        """
        if not text or len(text.strip()) < 20:
            return {"stored": False, "reason": "Text too short"}

        try:
            collection = _get_collection(profile_id)
            doc_id = f"mem_{uuid.uuid4().hex[:12]}"

            # Split long text into chunks (~500 chars each)
            chunks = self._chunk_text(text, max_chars=500)

            ids = []
            documents = []
            metadatas = []

            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_{i}"
                ids.append(chunk_id)
                documents.append(chunk)
                meta = {**(metadata or {}), "chunk_index": i, "total_chunks": len(chunks)}
                metadatas.append(meta)

            collection.add(ids=ids, documents=documents, metadatas=metadatas)

            logger.info(f"RAG: stored {len(chunks)} chunks for persona {profile_id[:8]}")
            return {"stored": True, "chunks": len(chunks), "doc_id": doc_id}

        except Exception as e:
            logger.error(f"RAG store failed: {e}")
            return {"stored": False, "error": str(e)}

    async def recall(
        self,
        profile_id: str,
        query: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant past analyses from the persona's memory.
        Returns list of {"text": str, "metadata": dict, "distance": float}
        """
        if not query or len(query.strip()) < 5:
            return []

        try:
            collection = _get_collection(profile_id)

            if collection.count() == 0:
                return []

            results = collection.query(
                query_texts=[query],
                n_results=min(top_k, collection.count()),
            )

            memories = []
            if results and results.get("documents"):
                for i, doc in enumerate(results["documents"][0]):
                    memories.append({
                        "text": doc,
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                        "distance": results["distances"][0][i] if results.get("distances") else 0,
                    })

            logger.info(f"RAG: recalled {len(memories)} memories for persona {profile_id[:8]}")
            return memories

        except Exception as e:
            logger.error(f"RAG recall failed: {e}")
            return []

    async def clear_memory(self, profile_id: str) -> Dict[str, Any]:
        """Wipe all stored memories for a persona."""
        try:
            client = _get_chroma_client()
            safe_name = f"persona_{profile_id.replace('-', '_')[:32]}"
            try:
                client.delete_collection(safe_name)
                logger.info(f"RAG: cleared memory for persona {profile_id[:8]}")
                return {"cleared": True}
            except ValueError:
                return {"cleared": True, "note": "Collection did not exist"}
        except Exception as e:
            logger.error(f"RAG clear failed: {e}")
            return {"cleared": False, "error": str(e)}

    async def get_memory_stats(self, profile_id: str) -> Dict[str, Any]:
        """Get stats about a persona's stored memory."""
        try:
            collection = _get_collection(profile_id)
            return {
                "profile_id": profile_id,
                "total_memories": collection.count(),
                "collection_name": collection.name,
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def _chunk_text(text: str, max_chars: int = 500) -> List[str]:
        """Split text into chunks at sentence boundaries."""
        sentences = text.replace("\n", " ").split(". ")
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            candidate = f"{current_chunk}. {sentence}" if current_chunk else sentence
            if len(candidate) > max_chars and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk = candidate

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks if chunks else [text[:max_chars]]


# Singleton
rag_service = RAGService()
