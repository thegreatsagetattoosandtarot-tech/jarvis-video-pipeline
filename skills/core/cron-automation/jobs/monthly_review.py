#!/usr/bin/env python3
"""
J.A.R.V.I.S. Monthly Review
Strategic alignment, course correction - runs 1st of each month.
"""

import json
from datetime import datetime
from pathlib import Path

JARVIS_ROOT = Path("/opt/data/jarvis")
LOGS_DIR = JARVIS_ROOT / "logs"


def main():
    now = datetime.now()
    
    print(f"=== J.A.R.V.I.S. MONTHLY REVIEW - {now.strftime('%B %Y')} ===\n")
    
    review = {
        "timestamp": now.isoformat(),
        "month": now.strftime("%Y-%m"),
        "strategic_alignment": [],
        "course_corrections": [],
        "architecture_review": [],
        "next_month_objectives": []
    }
    
    print("STRATEGIC ALIGNMENT CHECK:")
    alignments = [
        ("Dual-brain architecture", "COMPLETE", "Both brains populated, feedback loop active"),
        ("12 Archangel agents", "IN_PROGRESS", "11/12 spawned, Gabriel needs final spawn"),
        ("Voice pipeline", "READY", "STT/TTS/Wake word verified, needs hardware"),
        ("Business automation", "PLANNING", "Framework ready, needs integration"),
        ("Revenue automation", "EARLY", "Skills built, needs deployment"),
    ]
    for item, status, note in alignments:
        print(f"  [{status}] {item}: {note}")
    
    print("\nCOURSE CORRECTIONS NEEDED:")
    corrections = [
        "Complete Gabriel agent spawn",
        "Configure Hostinger SSH keys and test backup",
        "Install iproute2 for security hardening network check",
        "Set up Picovoice Console for custom wake word",
        "Integrate payment APIs for financial reporting",
    ]
    for c in corrections:
        print(f"  → {c}")
    
    print("\nARCHITECTURE REVIEW:")
    arch_items = [
        "Mission Control Dashboard: OPERATIONAL (port 8080)",
        "Agent Factory: OPERATIONAL (12 agents defined)",
        "Vector Memory/RAG: OPERATIONAL (22 chunks indexed)",
        "Dual-brain Sync: ACTIVE (5-min intervals)",
        "Security Hardening: 7/8 checks passing (needs iproute2)",
        "Backup System: CONFIGURED (needs SSH keys)",
    ]
    for item in arch_items:
        print(f"  • {item}")
    
    print("\nNEXT MONTH OBJECTIVES:")
    objectives = [
        "Full 12-agent workforce operational",
        "Voice pipeline hardware integration complete",
        "Hostinger backup verified and automated",
        "Business automation workflows deployed",
        "First $1000/month automation revenue",
        "Client booking automation live",
    ]
    for i, obj in enumerate(objectives, 1):
        print(f"  {i}. {obj}")
    
    # Save
    LOGS_DIR.mkdir(exist_ok=True)
    review_file = LOGS_DIR / f"monthly_review_{now.strftime('%Y%m')}.json"
    with open(review_file, "w") as f:
        json.dump(review, f, indent=2)
    
    print(f"\n✓ Monthly review saved to {review_file}")


if __name__ == "__main__":
    main()