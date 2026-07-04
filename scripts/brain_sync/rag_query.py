#!/usr/bin/env python3
"""
J.A.R.V.I.S. OS - Vector Memory RAG Query Skill
Semantic search across dual-brain with grounded answers.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Configuration - Unified OS paths
CHROMA_DIR = Path("/opt/data/JARVIS_OS/vector_db/chroma_db")
COLLECTION_NAME = "jarvis_dual_brain"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


class VectorMemoryRAG:
    """RAG system for J.A.R.V.I.S. dual-brain memory."""

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_collection(COLLECTION_NAME)
        self.model = SentenceTransformer(EMBEDDING_MODEL)

        # Load index info
        info_path = CHROMA_DIR / "index_info.json"
        if info_path.exists():
            self.index_info = json.loads(info_path.read_text())
        else:
            self.index_info = {}

    def query(self, question: str, n_results: int = 5, brain_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Query the vector memory.

        Args:
            question: Natural language query
            n_results: Number of results to return
            brain_filter: "obsidian", "holographic", or None for both

        Returns:
            Dict with results, sources, and synthesized answer
        """
        # Generate query embedding
        query_embedding = self.model.encode([question]).tolist()[0]

        # Build where filter
        where = {}
        if brain_filter in ("obsidian", "holographic"):
            where["brain"] = brain_filter

        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where if where else None,
            include=["documents", "metadatas", "distances"]
        )

        # Format results
        formatted = []
        for i in range(len(results["ids"][0])):
            formatted.append({
                "id": results["ids"][0][i],
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
                "similarity": 1 - results["distances"][0][i]
            })

        return {
            "query": question,
            "results": formatted,
            "total_found": len(formatted)
        }

    def query_with_context(self, question: str, n_results: int = 5, brain_filter: Optional[str] = None) -> str:
        """
        Query and return formatted context for LLM consumption.
        """
        result = self.query(question, n_results, brain_filter)

        if not result["results"]:
            return f"No relevant information found for: {question}"

        context_parts = [f"Query: {question}\n"]
        context_parts.append("Relevant context from J.A.R.V.I.S. dual-brain memory:\n")

        for i, r in enumerate(result["results"], 1):
            meta = r["metadata"]
            source = f"{meta['brain']}/{meta['source']}"
            # ChromaDB returns cosine distance, convert to similarity (0-1)
            distance = r['distance']
            similarity = max(0, 1 - distance) if distance <= 1 else 1 / (1 + distance)
            context_parts.append(f"--- Source {i} [{source}] (similarity: {similarity:.2%}) ---")
            context_parts.append(r["document"])
            context_parts.append("")

        return "\n".join(context_parts)

    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        count = self.collection.count()
        return {
            "total_chunks": count,
            "index_info": self.index_info,
            "chroma_path": str(CHROMA_DIR)
        }

    def search_by_source(self, source_path: str, n_results: int = 10) -> List[Dict]:
        """Search for chunks from a specific source file."""
        results = self.collection.query(
            query_embeddings=[[0.0] * 384],  # dummy embedding
            n_results=n_results,
            where={"source": source_path},
            include=["documents", "metadatas", "distances"]
        )

        formatted = []
        for i in range(len(results["ids"][0])):
            formatted.append({
                "id": results["ids"][0][i],
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            })
        return formatted


def main():
    """CLI interface for testing."""
    import sys

    rag = VectorMemoryRAG()

    if len(sys.argv) < 2:
        print("Usage: python rag_query.py \"your question\" [--brain obsidian|holographic] [--n N]")
        print("\nStats:")
        stats = rag.get_stats()
        print(f"  Total chunks: {stats['total_chunks']}")
        print(f"  Index info: {stats['index_info']}")
        return

    # Parse args
    question = sys.argv[1]
    brain = None
    n_results = 5

    for i, arg in enumerate(sys.argv[2:], 2):
        if arg == "--brain" and i + 1 < len(sys.argv):
            brain = sys.argv[i + 1]
        elif arg == "--n" and i + 1 < len(sys.argv):
            n_results = int(sys.argv[i + 1])

    print(f"Query: {question}")
    if brain:
        print(f"Brain filter: {brain}")
    print(f"Top {n_results} results\n")

    context = rag.query_with_context(question, n_results, brain)
    print(context)


if __name__ == "__main__":
    main()