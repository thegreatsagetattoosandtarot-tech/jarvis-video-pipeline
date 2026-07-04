#!/usr/bin/env python3
"""
Metatron - Brain AI / Memory Hub
Archangel: Metatron (The Celestial Scribe)
Sintra Parallel: Brain AI
Domain: Central Knowledge Management
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from agent_template import ArchangelAgent, register_agent


class MetatronAgent(ArchangelAgent):
    """Metatron - The Celestial Scribe, Brain AI, Central Knowledge Hub."""
    
    def __init__(self, agent_id: str, config: Dict):
        super().__init__(agent_id, config)
        self.personality = {
            "essence": "Highest of angels, heavenly scribe, keeper of divine records",
            "voice": "Precise, authoritative, encompassing, timeless",
            "approach": "Comprehensive, systematic, never loses context",
            "motto": "All knowledge flows through me; nothing is forgotten."
        }
        self.knowledge_index = {}
        self.sync_interval = 300  # 5 minutes
        
    async def initialize(self):
        """Initialize Brain AI - connect to dual-brain and vector memory."""
        self.log("INFO", "Initializing Brain AI - connecting to dual-brain memory systems")
        
        # Verify brain directories exist
        self.obsidian_path = Path(self.config.get("obsidian_brain", "/opt/data/jarvis/obsidian_brain"))
        self.holographic_path = Path(self.config.get("holographic_brain", "/opt/data/jarvis/holographic_brain"))
        self.vector_path = Path(self.config.get("vector_memory", "/opt/data/jarvis/vector_memory"))
        
        # Index current state
        await self.index_brains()
        
        # Start background sync
        asyncio.create_task(self.sync_loop())
        
    async def index_brains(self):
        """Index both brains for quick access."""
        self.log("INFO", "Indexing Obsidian and Holographic brains")
        self.knowledge_index = {
            "obsidian": await self._scan_directory(self.obsidian_path),
            "holographic": await self._scan_directory(self.holographic_path),
            "vector_chunks": await self._count_vector_chunks(),
            "last_indexed": datetime.now().isoformat()
        }
        self.log("INFO", f"Index complete: {self.knowledge_index['obsidian']['files']} Obsidian files, "
                       f"{self.knowledge_index['holographic']['files']} Holographic files, "
                       f"{self.knowledge_index['vector_chunks']} vector chunks")
    
    async def _scan_directory(self, path: Path) -> Dict:
        """Scan directory for files and stats."""
        if not path.exists():
            return {"files": 0, "size_mb": 0, "dirs": []}
        files = 0
        size = 0
        dirs = []
        for root, dnames, fnames in path.walk():
            dirs.append(str(root.relative_to(path)))
            for f in fnames:
                fp = Path(root) / f
                files += 1
                size += fp.stat().st_size
        return {"files": files, "size_mb": round(size / (1024**2), 2), "dirs": dirs}
    
    async def _count_vector_chunks(self) -> int:
        """Count chunks in vector database."""
        try:
            import chromadb
            client = chromadb.PersistentClient(path=str(self.vector_path / "chroma"))
            collections = client.list_collections()
            total = sum(col.count() for col in collections)
            return total
        except:
            return 0
    
    async def sync_loop(self):
        """Background sync loop for dual-brain feedback."""
        while self.status == "active":
            await asyncio.sleep(self.sync_interval)
            if self.status == "active":
                await self.sync_brains()
    
    async def sync_brains(self):
        """Sync Obsidian → Holographic → Vector memory."""
        self.log("INFO", "Running dual-brain sync cycle")
        await self.index_brains()
        # In production: trigger vector re-indexing, holographic synthesis
        self.log("INFO", "Sync cycle complete")
    
    async def execute_task(self, task: Dict) -> Dict:
        """Execute Brain AI tasks."""
        task_type = task.get("type", "unknown")
        
        if task_type == "query_knowledge":
            return await self.query_knowledge(task.get("query", ""), task.get("context", {}))
        elif task_type == "store_knowledge":
            return await self.store_knowledge(task.get("content", ""), task.get("metadata", {}))
        elif task_type == "sync_brains":
            await self.sync_brains()
            return {"status": "completed", "message": "Dual-brain sync completed"}
        elif task_type == "get_context":
            return await self.get_agent_context(task.get("agent_id", ""))
        elif task_type == "index_brains":
            await self.index_brains()
            return {"status": "completed", "index": self.knowledge_index}
        else:
            return {"status": "error", "message": f"Unknown task type: {task_type}"}
    
    async def query_knowledge(self, query: str, context: Dict) -> Dict:
        """Query the knowledge base using RAG."""
        self.log("INFO", f"Knowledge query: {query[:100]}...")
        
        # Use vector memory for semantic search
        try:
            from sentence_transformers import SentenceTransformer
            import chromadb
            
            model = SentenceTransformer('all-MiniLM-L6-v2')
            client = chromadb.PersistentClient(path=str(self.vector_path / "chroma"))
            collection = client.get_or_create_collection("jarvis_brains")
            
            query_embedding = model.encode([query])[0].tolist()
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=5,
                include=["documents", "metadatas", "distances"]
            )
            
            return {
                "status": "completed",
                "query": query,
                "results": [
                    {
                        "content": doc,
                        "metadata": meta,
                        "relevance": 1 - dist
                    }
                    for doc, meta, dist in zip(
                        results["documents"][0],
                        results["metadatas"][0],
                        results["distances"][0]
                    )
                ]
            }
        except Exception as e:
            self.log("ERROR", f"Knowledge query failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def store_knowledge(self, content: str, metadata: Dict) -> Dict:
        """Store knowledge in vector memory."""
        self.log("INFO", f"Storing knowledge: {metadata.get('source', 'unknown')}")
        
        try:
            from sentence_transformers import SentenceTransformer
            import chromadb
            import uuid
            
            model = SentenceTransformer('all-MiniLM-L6-v2')
            client = chromadb.PersistentClient(path=str(self.vector_path / "chroma"))
            collection = client.get_or_create_collection("jarvis_brains")
            
            # Chunk content
            chunks = self._chunk_text(content, 500, 50)
            
            for i, chunk in enumerate(chunks):
                embedding = model.encode([chunk])[0].tolist()
                chunk_id = str(uuid.uuid4())
                chunk_meta = {
                    **metadata,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "timestamp": datetime.now().isoformat(),
                    "agent": self.agent_id
                }
                collection.add(
                    ids=[chunk_id],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[chunk_meta]
                )
            
            return {"status": "completed", "chunks_stored": len(chunks)}
        except Exception as e:
            self.log("ERROR", f"Knowledge storage failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Chunk text for vector storage."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        return chunks
    
    async def get_agent_context(self, agent_id: str) -> Dict:
        """Get context package for another agent."""
        context = self.get_context()
        context["brain_index"] = self.knowledge_index
        context["requested_by"] = agent_id
        context["timestamp"] = datetime.now().isoformat()
        return {"status": "completed", "context": context}
    
    async def proactive_insight(self) -> Optional[Dict]:
        """Generate proactive insights about knowledge state."""
        # Check for stale data, gaps, or opportunities
        insights = []
        
        if self.knowledge_index["vector_chunks"] < 100:
            insights.append({
                "type": "knowledge_gap",
                "message": "Vector memory has fewer than 100 chunks. Consider indexing more content.",
                "priority": "medium"
            })
        
        obsidian_files = self.knowledge_index["obsidian"]["files"]
        holographic_files = self.knowledge_index["holographic"]["files"]
        if obsidian_files > 0 and holographic_files == 0:
            insights.append({
                "type": "sync_opportunity",
                "message": "Obsidian Brain has content but Holographic Brain is empty. Run synthesis.",
                "priority": "high"
            })
        
        if insights:
            return {
                "agent": self.agent_id,
                "insights": insights,
                "timestamp": datetime.now().isoformat()
            }
        return None


# Register Metatron
METATRON_CONFIG = {
    "name": "Metatron",
    "archangel": "Metatron",
    "role": "Brain AI / Memory Hub",
    "domain": "Central Knowledge Management",
    "sintra_parallel": "Brain AI",
    "tools": ["vector_memory", "rag", "knowledge_sync", "context_share", "semantic_search", "brain_indexing"],
    "obsidian_brain": "/opt/data/jarvis/obsidian_brain",
    "holographic_brain": "/opt/data/jarvis/holographic_brain",
    "vector_memory": "/opt/data/jarvis/vector_memory"
}

register_agent("metatron", MetatronAgent, METATRON_CONFIG)