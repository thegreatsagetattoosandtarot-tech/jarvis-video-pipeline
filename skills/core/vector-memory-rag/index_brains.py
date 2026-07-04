#!/usr/bin/env python3
"""
J.A.R.V.I.S. Vector Memory / RAG System
Indexes all .md files in dual-brain architecture for semantic search.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Configuration
OBSIDIAN_BRAIN = Path("/opt/data/jarvis/obsidian_brain")
HOLOGRAPHIC_BRAIN = Path("/opt/data/jarvis/holographic_brain")
CHROMA_DIR = Path("/opt/data/jarvis/vector_memory")
COLLECTION_NAME = "jarvis_dual_brain"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Fast, good quality, 384-dim

def get_md_files(brain_path: Path) -> List[Path]:
    """Get all .md files recursively."""
    return list(brain_path.rglob("*.md"))

def read_file_content(filepath: Path) -> str:
    """Read file content with error handling."""
    try:
        return filepath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return ""

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks

def build_metadata(filepath: Path, brain_type: str, chunk_idx: int, total_chunks: int) -> Dict[str, Any]:
    """Build metadata for a chunk."""
    rel_path = filepath.relative_to(OBSIDIAN_BRAIN if brain_type == "obsidian" else HOLOGRAPHIC_BRAIN)
    return {
        "source": str(rel_path),
        "brain": brain_type,
        "absolute_path": str(filepath),
        "chunk_index": chunk_idx,
        "total_chunks": total_chunks,
        "file_name": filepath.name,
        "file_stem": filepath.stem,
        "parent_dir": filepath.parent.name,
    }

def index_brain(brain_path: Path, brain_type: str, collection, model) -> int:
    """Index all .md files in a brain."""
    md_files = get_md_files(brain_path)
    print(f"[{brain_type.upper()}] Found {len(md_files)} .md files")
    
    total_chunks = 0
    for filepath in md_files:
        content = read_file_content(filepath)
        if not content.strip():
            continue
        
        chunks = chunk_text(content)
        if not chunks:
            continue
        
        # Generate embeddings
        embeddings = model.encode(chunks, show_progress_bar=False).tolist()
        
        # Prepare data for ChromaDB
        ids = [f"{brain_type}_{filepath.stem}_{i}" for i in range(len(chunks))]
        metadatas = [build_metadata(filepath, brain_type, i, len(chunks)) for i in range(len(chunks))]
        
        # Add to collection
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )
        
        total_chunks += len(chunks)
        print(f"  {filepath.relative_to(brain_path)}: {len(chunks)} chunks")
    
    return total_chunks

def main():
    print("=" * 60)
    print("J.A.R.V.I.S. Vector Memory / RAG Initialization")
    print("=" * 60)
    
    # Initialize ChromaDB
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR),
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Get or create collection
    try:
        collection = client.get_collection(COLLECTION_NAME)
        print(f"Collection '{COLLECTION_NAME}' exists, clearing...")
        client.delete_collection(COLLECTION_NAME)
        collection = client.create_collection(COLLECTION_NAME)
    except:
        collection = client.create_collection(COLLECTION_NAME)
    
    print(f"Collection '{COLLECTION_NAME}' ready")
    
    # Load embedding model
    print(f"Loading embedding model: {EMBEDDING_MODEL}...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print("Model loaded")
    
    # Index both brains
    print("\n--- Indexing Obsidian Brain ---")
    obsidian_chunks = index_brain(OBSIDIAN_BRAIN, "obsidian", collection, model)
    
    print("\n--- Indexing Holographic Brain ---")
    holographic_chunks = index_brain(HOLOGRAPHIC_BRAIN, "holographic", collection, model)
    
    print("\n" + "=" * 60)
    print("INDEXING COMPLETE")
    print("=" * 60)
    print(f"Obsidian Brain chunks: {obsidian_chunks}")
    print(f"Holographic Brain chunks: {holographic_chunks}")
    print(f"Total chunks indexed: {obsidian_chunks + holographic_chunks}")
    print(f"Collection count: {collection.count()}")
    print(f"Vector DB location: {CHROMA_DIR}")
    
    # Save index metadata
    index_info = {
        "collection_name": COLLECTION_NAME,
        "embedding_model": EMBEDDING_MODEL,
        "obsidian_chunks": obsidian_chunks,
        "holographic_chunks": holographic_chunks,
        "total_chunks": obsidian_chunks + holographic_chunks,
        "chroma_path": str(CHROMA_DIR),
        "brains": {
            "obsidian": str(OBSIDIAN_BRAIN),
            "holographic": str(HOLOGRAPHIC_BRAIN)
        }
    }
    (CHROMA_DIR / "index_info.json").write_text(json.dumps(index_info, indent=2))
    print("Index metadata saved to index_info.json")

if __name__ == "__main__":
    main()