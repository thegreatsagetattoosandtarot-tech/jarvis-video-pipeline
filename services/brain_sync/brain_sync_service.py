#!/usr/bin/env python3
"""
J.A.R.V.I.S. OS - Brain Sync Service
Continuous synchronization between Obsidian Brain, Holographic Brain, and Vector Memory.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Configuration
OBSIDIAN_BRAIN = Path("/opt/data/JARVIS_OS/brains/obsidian")
HOLOGRAPHIC_BRAIN = Path("/opt/data/JARVIS_OS/brains/holographic")
CHROMA_DIR = Path("/opt/data/JARVIS_OS/vector_db/chroma_db")
COLLECTION_NAME = "jarvis_dual_brain"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
SYNC_INTERVAL = 300  # 5 minutes


class BrainFileHandler(FileSystemEventHandler):
    """Watch for file changes in brain directories."""

    def __init__(self, sync_service):
        self.sync_service = sync_service
        self.pending_changes = set()

    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(".md"):
            self.pending_changes.add(event.src_path)

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(".md"):
            self.pending_changes.add(event.src_path)

    def on_deleted(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(".md"):
            self.sync_service.handle_deletion(event.src_path)


class BrainSyncService:
    """Main brain synchronization service."""

    def __init__(self):
        self.running = False
        self.observer = None
        self.client = None
        self.collection = None
        self.model = None
        self.last_sync = None
        self.sync_stats = {
            "total_syncs": 0,
            "files_indexed": 0,
            "chunks_created": 0,
            "errors": 0
        }

    async def initialize(self):
        """Initialize the sync service."""
        print("Initializing Brain Sync Service...")

        # Initialize ChromaDB
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False)
        )

        try:
            self.collection = self.client.get_collection(COLLECTION_NAME)
        except:
            self.collection = self.client.create_collection(COLLECTION_NAME)

        # Load embedding model
        self.model = SentenceTransformer(EMBEDDING_MODEL)

        # Setup file watchers
        self.observer = Observer()
        handler = BrainFileHandler(self)
        self.observer.schedule(handler, str(OBSIDIAN_BRAIN), recursive=True)
        self.observer.schedule(handler, str(HOLOGRAPHIC_BRAIN), recursive=True)
        self.observer.start()

        print("Brain Sync Service initialized")

    async def start(self):
        """Start the sync loop."""
        self.running = True
        print("Starting Brain Sync Service...")

        # Initial full sync
        await self.full_sync()

        # Background sync loop
        while self.running:
            try:
                await asyncio.sleep(SYNC_INTERVAL)
                if self.running:
                    await self.incremental_sync()
            except Exception as e:
                print(f"Sync loop error: {e}")
                self.sync_stats["errors"] += 1
                await asyncio.sleep(60)  # Back off on error

    def stop(self):
        """Stop the sync service."""
        self.running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()
        print("Brain Sync Service stopped")

    async def full_sync(self):
        """Full re-index of both brains."""
        print("Running full brain sync...")
        start_time = time.time()

        # Clear collection
        try:
            self.client.delete_collection(COLLECTION_NAME)
        except:
            pass
        self.collection = self.client.create_collection(COLLECTION_NAME)

        # Index both brains
        obsidian_chunks = await self._index_brain(OBSIDIAN_BRAIN, "obsidian")
        holographic_chunks = await self._index_brain(HOLOGRAPHIC_BRAIN, "holographic")

        total_chunks = obsidian_chunks + holographic_chunks
        elapsed = time.time() - start_time

        self.last_sync = datetime.now().isoformat()
        self.sync_stats["total_syncs"] += 1
        self.sync_stats["files_indexed"] += obsidian_chunks + holographic_chunks
        self.sync_stats["chunks_created"] += total_chunks

        print(f"Full sync complete: {total_chunks} chunks in {elapsed:.1f}s")
        print(f"  Obsidian: {obsidian_chunks} chunks")
        print(f"  Holographic: {holographic_chunks} chunks")

        # Save sync metadata
        await self._save_sync_metadata()

    async def incremental_sync(self):
        """Incremental sync - check for changes."""
        print("Running incremental sync check...")

        # For now, just do a quick verification
        count = self.collection.count()
        if count == 0:
            print("Collection empty, running full sync...")
            await self.full_sync()
        else:
            print(f"Collection has {count} chunks - verified")

        self.last_sync = datetime.now().isoformat()
        self.sync_stats["total_syncs"] += 1
        await self._save_sync_metadata()

    async def _index_brain(self, brain_path: Path, brain_type: str) -> int:
        """Index all .md files in a brain."""
        if not brain_path.exists():
            print(f"Brain path does not exist: {brain_path}")
            return 0

        md_files = list(brain_path.rglob("*.md"))
        total_chunks = 0

        for filepath in md_files:
            try:
                content = filepath.read_text(encoding="utf-8")
                if not content.strip():
                    continue

                chunks = self._chunk_text(content)
                if not chunks:
                    continue

                # Generate embeddings
                embeddings = self.model.encode(chunks, show_progress_bar=False).tolist()

                # Build metadata
                rel_path = filepath.relative_to(brain_path)
                metadatas = []
                for i in range(len(chunks)):
                    metadatas.append({
                        "source": str(rel_path),
                        "brain": brain_type,
                        "absolute_path": str(filepath),
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "file_name": filepath.name,
                        "file_stem": filepath.stem,
                        "parent_dir": filepath.parent.name,
                    })

                ids = [f"{brain_type}_{filepath.stem}_{i}" for i in range(len(chunks))]

                # Add to collection
                self.collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    documents=chunks,
                    metadatas=metadatas
                )

                total_chunks += len(chunks)

            except Exception as e:
                print(f"Error indexing {filepath}: {e}")
                self.sync_stats["errors"] += 1

        return total_chunks

    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> list:
        """Split text into overlapping chunks."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        return chunks

    def handle_deletion(self, filepath: str):
        """Handle file deletion - remove from vector DB."""
        try:
            # Find and delete chunks from this file
            results = self.collection.get(
                where={"absolute_path": filepath},
                include=["ids"]
            )
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
                print(f"Removed {len(results['ids'])} chunks for deleted file: {filepath}")
        except Exception as e:
            print(f"Error handling deletion: {e}")

    async def _save_sync_metadata(self):
        """Save sync metadata to disk."""
        metadata = {
            "last_sync": self.last_sync,
            "stats": self.sync_stats,
            "chroma_count": self.collection.count() if self.collection else 0
        }
        (CHROMA_DIR / "sync_metadata.json").write_text(json.dumps(metadata, indent=2))


async def main():
    """Run the brain sync service."""
    service = BrainSyncService()
    await service.initialize()
    try:
        await service.start()
    except KeyboardInterrupt:
        service.stop()


if __name__ == "__main__":
    asyncio.run(main())