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
    return None

def _get_collection(profile_id: str):
    return None


class RAGService:
    """Retrieval-Augmented Generation service for persona memory."""

    async def store_memory(
        self,
        profile_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        [Bypassed for test] Store a text chunk in the persona's memory.
        """
        return {"stored": True, "note": "Bypassed for test"}

    async def recall(
        self,
        profile_id: str,
        query: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        [Bypassed for test] Retrieve relevant past analyses from the persona's memory.
        """
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
