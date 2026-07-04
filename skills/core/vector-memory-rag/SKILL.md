---
name: vector-memory-rag
description: Semantic search and RAG across J.A.R.V.I.S. dual-brain memory (Obsidian + Holographic). Provides grounded answers with source citations.
category: memory
---

# Vector Memory RAG Skill

## Overview
This skill provides semantic search across all indexed memory files in the J.A.R.V.I.S. dual-brain architecture. It uses ChromaDB for vector storage and sentence-transformers (all-MiniLM-L6-v2) for embeddings.

## Components
- **Indexer** (`/opt/data/jarvis/scripts/index_brains.py`): Indexes all `.md` files in both brains
- **Query Engine** (`/opt/data/jarvis/scripts/rag_query.py`): Semantic search with RAG context generation
- **Vector DB**: ChromaDB at `/opt/data/jarvis/vector_memory/`

## Usage

### Index/Re-index Brains
```bash
/opt/data/jarvis/venv/bin/python /opt/data/jarvis/scripts/index_brains.py
```

### Query Memory
```bash
# Basic query
/opt/data/jarvis/venv/bin/python /opt/data/jarvis/scripts/rag_query.py "your question"

# With brain filter
/opt/data/jarvis/venv/bin/python /opt/data/jarvis/scripts/rag_query.py "your question" --brain obsidian

# More results
/opt/data/jarvis/venv/bin/python /opt/data/jarvis/scripts/rag_query.py "your question" --n 10
```

### Python API
```python
from scripts.rag_query import VectorMemoryRAG

rag = VectorMemoryRAG()

# Get structured results
result = rag.query("What is my business?", n_results=5, brain_filter="obsidian")

# Get formatted context for LLM
context = rag.query_with_context("What are my priorities?", n_results=5)

# Get stats
stats = rag.get_stats()
```

## Configuration
- **Embedding Model**: all-MiniLM-L6-v2 (384 dimensions, fast, good quality)
- **Chunk Size**: 500 words with 50 word overlap
- **Collection**: jarvis_dual_brain
- **Brains Indexed**: 
  - Obsidian: `/opt/data/jarvis/obsidian_brain/`
  - Holographic: `/opt/data/jarvis/holographic_brain/`

## Current Status
- ✅ Dependencies installed (chromadb, sentence-transformers)
- ✅ Virtual environment at `/opt/data/jarvis/venv/`
- ✅ Obsidian Brain indexed (16 chunks from 7 files)
- ⏳ Holographic Brain empty (0 files, 0 chunks)
- ✅ Query engine functional with similarity scoring
- ✅ RAG context generation working

## Next Steps
1. Add Holographic Brain content (case studies, scenarios, outcomes)
2. Create auto-reindex on file changes (watchdog or cron)
3. Add hybrid search (keyword + vector)
4. Integrate with Hermes skill system for direct tool access
5. Add embedding model upgrade path (e.g., all-mpnet-base-v2 for higher quality)