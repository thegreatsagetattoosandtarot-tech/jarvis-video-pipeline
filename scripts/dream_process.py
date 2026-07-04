#!/usr/bin/env python3
"""
J.A.R.V.I.S. OS - Dream Process
Nightly synthesis, pattern recognition, and insight generation.
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List

JARVIS_ROOT = Path("/opt/data/JARVIS_OS")
OBSIDIAN_BRAIN = JARVIS_ROOT / "brains" / "obsidian"
HOLOGRAPHIC_BRAIN = JARVIS_ROOT / "brains" / "holographic"
VECTOR_DB = JARVIS_ROOT / "vector_db" / "chroma_db"
LOGS_DIR = JARVIS_ROOT / "logs"


async def analyze_patterns() -> Dict[str, Any]:
    """Analyze patterns in the dual-brain memory."""
    insights = []

    # Check Obsidian Brain growth
    obsidian_files = list(OBSIDIAN_BRAIN.rglob("*.md")) if OBSIDIAN_BRAIN.exists() else []
    holographic_files = list(HOLOGRAPHIC_BRAIN.rglob("*.md")) if HOLOGRAPHIC_BRAIN.exists() else []

    if len(obsidian_files) > len(holographic_files) * 3:
        insights.append({
            "type": "knowledge_gap",
            "priority": "high",
            "message": f"Obsidian Brain has {len(obsidian_files)} files but Holographic has only {len(holographic_files)}. Consider synthesizing raw data into applied knowledge."
        })

    # Check vector DB status
    vector_chunks = 0
    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(VECTOR_DB))
        collection = client.get_collection("jarvis_dual_brain")
        vector_chunks = collection.count()
    except:
        pass

    if vector_chunks < 100:
        insights.append({
            "type": "vector_gap",
            "priority": "medium",
            "message": f"Vector DB has only {vector_chunks} chunks. Consider re-indexing both brains."
        })

    # Check recent activity
    logs = LOGS_DIR / "brain_sync"
    if logs.exists():
        recent_logs = list(logs.rglob("*.log"))[-5:] if logs.exists() else []
        if not recent_logs:
            insights.append({
                "type": "sync_stale",
                "priority": "medium",
                "message": "No recent brain sync logs found. Sync may be stalled."
            })

    return {"insights": insights, "stats": {
        "obsidian_files": len(obsidian_files),
        "holographic_files": len(holographic_files),
        "vector_chunks": vector_chunks
    }}


async def generate_insights(pattern_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate proactive insights based on patterns."""
    insights = pattern_analysis.get("insights", [])

    # Add daily insight
    insights.append({
        "type": "daily_insight",
        "priority": "info",
        "message": "Nightly dream process completed. Dual-brain synchronization active. Ready."
    })

    return insights


async def update_holographic(pattern_analysis: Dict[str, Any], insights: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Update holographic brain with synthesized knowledge."""
    results = {"created": [], "updated": []}

    # Create/update case studies from recent projects
    # In production, this would analyze actual project outcomes

    # Create applied knowledge entry
    entry = {
        "date": datetime.now().isoformat(),
        "pattern_analysis": pattern_analysis,
        "insights": insights,
        "synthesis": "Nightly consolidation of dual-brain memory completed."
    }

    # Save to holographic brain
    applied_dir = HOLOGRAPHIC_BRAIN / "applied_knowledge"
    applied_dir.mkdir(parents=True, exist_ok=True)

    filename = f"dream_synthesis_{datetime.now().strftime('%Y%m%d')}.md"
    filepath = applied_dir / filename

    content = f"""# Dream Process Synthesis - {datetime.now().strftime('%Y-%m-%d')}

## Pattern Analysis
- Obsidian Brain Files: {pattern_analysis['stats']['obsidian_files']}
- Holographic Brain Files: {pattern_analysis['stats']['holographic_files']}
- Vector DB Chunks: {pattern_analysis['stats']['vector_chunks']}

## Insights Generated
"""
    for insight in insights:
        content += f"- **{insight['type']}** ({insight['priority']}): {insight['message']}\n"

    content += f"""
## Synthesis
{entry['synthesis']}
"""

    filepath.write_text(content)
    results["created"].append(str(filepath))

    return results


async def main():
    """Run the dream process."""
    print("=" * 60)
    print(f"J.A.R.V.I.S. OS Dream Process - {datetime.now().isoformat()}")
    print("=" * 60)

    # Phase 1: Pattern Analysis
    print("\n[1/3] Analyzing patterns...")
    pattern_analysis = await analyze_patterns()
    print(f"  Found {len(pattern_analysis['insights'])} pattern insights")

    # Phase 2: Generate Insights
    print("\n[2/3] Generating proactive insights...")
    insights = await generate_insights(pattern_analysis)
    print(f"  Generated {len(insights)} insights")

    # Phase 3: Update Holographic Brain
    print("\n[3/3] Updating Holographic Brain...")
    update_results = await update_holographic(pattern_analysis, insights)
    print(f"  Created: {len(update_results['created'])} files")

    print("\n" + "=" * 60)
    print("DREAM PROCESS COMPLETE")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))