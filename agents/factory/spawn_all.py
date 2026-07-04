#!/usr/bin/env python3
"""
Archangel Agent Factory - Spawn All Agents
Creates and initializes all 12 archangel agents.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add the factory to path
sys.path.insert(0, str(Path(__file__).parent))

from agent_template import AGENT_REGISTRY, list_agents

# Import all agent modules (they self-register)
try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "archangels"))
    import metatron, gabriel, raphael, uriel, sandalphon, jophiel
    import michael, raguel, remiel, sariel, azrael, chamuel
except ImportError:
    # Modules don't exist yet - will create them
    pass


async def spawn_agent(agent_id: str) -> bool:
    """Spawn a single agent by ID."""
    if agent_id not in AGENT_REGISTRY:
        print(f"Agent {agent_id} not registered")
        return False

    agent_class, config = AGENT_REGISTRY[agent_id]
    agent = agent_class(agent_id, config)

    try:
        await agent.start()
        print(f"✓ Spawned {agent.name} ({agent.archangel}) - {agent.role}")

        # Save agent process info
        agent_info = {
            "agent_id": agent_id,
            "name": agent.name,
            "archangel": agent.archangel,
            "role": agent.role,
            "domain": agent.domain,
            "status": "active",
            "pid": os.getpid(),
            "session_id": agent.session_id
        }

        agent_dir = Path("/opt/data/JARVIS_OS/agents/factory") / agent_id
        agent_dir.mkdir(parents=True, exist_ok=True)
        with open(agent_dir / "process.json", "w") as f:
            json.dump(agent_info, f, indent=2)

        return True
    except Exception as e:
        print(f"✗ Failed to spawn {agent_id}: {e}")
        return False


async def spawn_all():
    """Spawn all 12 archangel agents."""
    print("=" * 60)
    print("J.A.R.V.I.S. ARCHANGEL AGENT FACTORY")
    print("Spawning 12 Archangel Agents")
    print("=" * 60)

    # Define all agent configs
    agents_config = [
        ("metatron", "Metatron", "Metatron", "Brain AI / Memory Hub", "Central Knowledge Management", "Brain AI",
         ["vector_memory", "rag", "knowledge_sync", "context_share", "semantic_search", "brain_indexing"]),
        ("gabriel", "Gabriel", "Gabriel", "Communication / Content", "Copywriting & Content", "Penn (Copywriter)",
         ["web_search", "content_gen", "social_media", "copywriting", "persuasive_writing", "brand_voice"]),
        ("raphael", "Raphael", "Raphael", "Support / Healing", "Customer Support", "Cassie (Customer Support)",
         ["email", "ticketing", "faq_gen", "routing", "empathy_engine", "resolution_tracking"]),
        ("uriel", "Uriel", "Uriel", "Research / Analysis", "Data Analysis", "Dexter (Data Analyst)",
         ["web_search", "data_analysis", "visualization", "forecasting", "pattern_recognition", "statistical_modeling"]),
        ("sandalphon", "Sandalphon", "Sandalphon", "Social / Community", "Social Media Management", "Soshie (Social Media)",
         ["social_scheduling", "content_calendar", "engagement", "analytics", "community_building", "trend_monitoring"]),
        ("jophiel", "Jophiel", "Jophiel", "Marketing / Beauty", "Email Marketing", "Emmie (Email Marketing)",
         ["email_campaigns", "automation", "ab_testing", "optimization", "segmentation", "deliverability"]),
        ("michael", "Michael", "Michael", "Leadership / Strategy", "Business Strategy", "—",
         ["strategic_planning", "decision_support", "risk_analysis", "roadmap", "competitive_intel", "okr_tracking"]),
        ("raguel", "Raguel", "Raguel", "Security / Compliance", "Security & Compliance", "—",
         ["security_audit", "compliance", "penetration_testing", "monitoring", "threat_modeling", "incident_response"]),
        ("remiel", "Remiel", "Remiel", "Creative / Vision", "Video & Creative", "Vince (Video)",
         ["video_gen", "editing", "storyboarding", "motion_graphics", "visual_storytelling", "brand_visuals"]),
        ("sariel", "Sariel", "Sariel", "Knowledge / Learning", "Research & Learning", "—",
         ["deep_research", "osint", "synthesis", "knowledge_base", "fact_checking", "source_verification"]),
        ("azrael", "Azrael", "Azrael", "Archival / Cleanup", "Archive & Maintenance", "—",
         ["archival", "cleanup", "retention", "deduplication", "data_lifecycle", "compliance_archival"]),
        ("chamuel", "Chamuel", "Chamuel", "Relationships / HR / Ops", "Operations & Relationships", "—",
         ["crm", "scheduling", "hr", "vendor_mgmt", "partnership_dev", "team_coordination"])
    ]

    # Register any missing agents
    for agent_id, name, archangel, role, domain, sintra_parallel, tools in agents_config:
        if agent_id not in AGENT_REGISTRY:
            # Create a generic agent class for now
            config = {
                "name": name,
                "archangel": archangel,
                "role": role,
                "domain": domain,
                "sintra_parallel": sintra_parallel,
                "tools": tools
            }
            # We'll use MetatronAgent as base for now, but each should have its own
            import metatron
            AGENT_REGISTRY[agent_id] = (metatron.MetatronAgent, config)

    # Spawn all agents
    results = []
    for agent_id, name, archangel, role, domain, sintra_parallel, tools in agents_config:
        print(f"\nSpawning {name} ({archangel})...")
        success = await spawn_agent(agent_id)
        results.append((agent_id, name, success))

    # Summary
    print("\n" + "=" * 60)
    print("SPAWN SUMMARY")
    print("=" * 60)
    for agent_id, name, success in results:
        status = "✓ ACTIVE" if success else "✗ FAILED"
        print(f"  {status} - {name} ({agent_id})")

    active_count = sum(1 for _, _, s in results if s)
    print(f"\nTotal: {active_count}/12 agents active")

    # Save registry
    registry_file = Path("/opt/data/JARVIS_OS/agents/factory/registry.json")
    with open(registry_file, "w") as f:
        json.dump({
            "spawned_at": str(asyncio.get_event_loop().time()),
            "agents": [
                {"agent_id": aid, "name": name, "active": success}
                for aid, name, success in results
            ]
        }, f, indent=2)

    return active_count == 12


async def stop_all():
    """Stop all agents."""
    print("Stopping all agents...")
    agents_dir = Path("/opt/data/JARVIS_OS/agents/factory")
    for agent_dir in agents_dir.iterdir():
        if agent_dir.is_dir():
            process_file = agent_dir / "process.json"
            if process_file.exists():
                print(f"  Stopping {agent_dir.name}...")
                # In production, send stop signal to agent process


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Archangel Agent Factory")
    parser.add_argument("--spawn-all", action="store_true", help="Spawn all 12 agents")
    parser.add_argument("--stop-all", action="store_true", help="Stop all agents")
    parser.add_argument("--list", action="store_true", help="List registered agents")
    parser.add_argument("--agent", help="Spawn specific agent")

    args = parser.parse_args()

    if args.list:
        print("Registered Agents:")
        for agent in list_agents():
            print(f"  {agent['agent_id']}: {agent['name']} ({agent['archangel']}) - {agent['role']}")
    elif args.spawn_all:
        asyncio.run(spawn_all())
    elif args.stop_all:
        asyncio.run(stop_all())
    elif args.agent:
        asyncio.run(spawn_agent(args.agent))
    else:
        parser.print_help()