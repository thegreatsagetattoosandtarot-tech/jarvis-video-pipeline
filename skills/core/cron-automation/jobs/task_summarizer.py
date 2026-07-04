#!/usr/bin/env python3
"""
J.A.R.V.I.S. Task Summarizer
Daily task summary from task queue.
"""

import json
from datetime import datetime
from pathlib import Path

JARVIS_ROOT = Path("/opt/data/jarvis")
LOGS_DIR = JARVIS_ROOT / "logs"
CONFIG_DIR = JARVIS_ROOT / "config"


def main():
    print(f"=== J.A.R.V.I.S. TASK SUMMARY - {datetime.now().strftime('%B %d, %Y')} ===\n")
    
    # Read agent statuses
    agents_dir = CONFIG_DIR / "agents"
    active_agents = []
    if agents_dir.exists():
        for agent_dir in agents_dir.iterdir():
            if agent_dir.is_dir():
                status_file = agent_dir / "status.json"
                if status_file.exists():
                    with open(status_file) as f:
                        status = json.load(f)
                        if status.get("status") == "active":
                            active_agents.append(status)
    
    print(f"ACTIVE AGENTS ({len(active_agents)}):")
    for agent in active_agents:
        print(f"  • {agent.get('name')} ({agent.get('archangel')}) - {agent.get('role')}")
    
    # Pending tasks (placeholder)
    print("\nTODAY'S PRIORITIES:")
    priorities = [
        "Complete 12-agent workforce (1/12 remaining)",
        "Configure Hostinger SSH keys for backup",
        "Install iproute2 for network monitoring",
        "Set up Picovoice custom wake word",
        "Test voice pipeline with hardware",
    ]
    for i, p in enumerate(priorities, 1):
        print(f"  {i}. {p}")
    
    # Recurring tasks
    print("\nRECURRING DAILY:")
    recurring = [
        "Daily report (06:00)",
        "Weather summary (06:15)",
        "Task summary (08:00)",
        "Stock report (09:30 market days)",
        "Financial report (18:00)",
        "Nightly audit (02:00)",
        "Dream process (03:00)",
        "Hostinger backup (04:00)",
        "Vector re-index (05:00)",
    ]
    for r in recurring:
        print(f"  ☐ {r}")
    
    # Save
    LOGS_DIR.mkdir(exist_ok=True)
    task_file = LOGS_DIR / f"task_summary_{datetime.now().strftime('%Y%m%d')}.json"
    with open(task_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "active_agents": len(active_agents),
            "priorities": priorities
        }, f, indent=2)
    
    print(f"\n✓ Task summary saved to {task_file}")


if __name__ == "__main__":
    main()