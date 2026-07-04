#!/usr/bin/env python3
"""
J.A.R.V.I.S. Daily Report Generator
Morning briefing with weather, tasks, calendar, and system status.
"""

import os
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

JARVIS_ROOT = Path("/opt/data/jarvis")
CONFIG_DIR = JARVIS_ROOT / "config"
LOGS_DIR = JARVIS_ROOT / "logs"
OBSIDIAN_BRAIN = JARVIS_ROOT / "obsidian_brain"
HOLOGRAPHIC_BRAIN = JARVIS_ROOT / "holographic_brain"


def run_cmd(cmd: list) -> str:
    """Run command and return output."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"


def get_system_health() -> dict:
    """Get system health metrics."""
    import psutil
    
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "cpu_percent": cpu,
        "memory_percent": memory.percent,
        "memory_used_gb": round(memory.used / (1024**3), 2),
        "memory_total_gb": round(memory.total / (1024**3), 2),
        "disk_percent": round(disk.used / disk.total * 100, 1),
        "disk_used_gb": round(disk.used / (1024**3), 2),
        "disk_total_gb": round(disk.total / (1024**3), 2),
    }


def get_brain_status() -> dict:
    """Get dual-brain status."""
    def count_files(path: Path):
        if not path.exists():
            return {"files": 0, "size_mb": 0}
        files = 0
        size = 0
        for f in path.rglob("*"):
            if f.is_file():
                files += 1
                size += f.stat().st_size
        return {"files": files, "size_mb": round(size / (1024**2), 2)}
    
    return {
        "obsidian": count_files(OBSIDIAN_BRAIN),
        "holographic": count_files(HOLOGRAPHIC_BRAIN),
        "vector_chunks": 0,  # Would query chromadb
    }


def get_agent_status() -> dict:
    """Get agent status from config."""
    agents_dir = CONFIG_DIR / "agents"
    agents = {}
    if agents_dir.exists():
        for agent_dir in agents_dir.iterdir():
            if agent_dir.is_dir():
                status_file = agent_dir / "status.json"
                if status_file.exists():
                    with open(status_file) as f:
                        agents[agent_dir.name] = json.load(f)
    return agents


def get_today_appointments() -> list:
    """Get today's appointments (placeholder - integrate with Google Calendar)."""
    # TODO: Integrate with Google Calendar API
    return []


def get_pending_tasks() -> list:
    """Get pending tasks from task queue."""
    # TODO: Integrate with actual task queue
    return []


def generate_report() -> str:
    """Generate the daily report."""
    now = datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    time_str = now.strftime("%I:%M %p")
    
    health = get_system_health()
    brains = get_brain_status()
    agents = get_agent_status()
    appointments = get_today_appointments()
    tasks = get_pending_tasks()
    
    active_agents = sum(1 for a in agents.values() if a.get("status") == "active")
    total_agents = len(agents)
    
    report = f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    J.A.R.V.I.S. DAILY BRIEFING                              ║
║                         {date_str} @ {time_str}                              ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ SYSTEM HEALTH                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ CPU:      {health['cpu_percent']:>5.1f}%                                                    ║
║ Memory:   {health['memory_percent']:>5.1f}% ({health['memory_used_gb']:.1f}/{health['memory_total_gb']:.1f} GB)                      ║
║ Disk:     {health['disk_percent']:>5.1f}% ({health['disk_used_gb']:.1f}/{health['disk_total_gb']:.1f} GB)                      ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ DUAL-BRAIN STATUS                                                           ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Obsidian Brain:    {brains['obsidian']['files']:>4} files  ({brains['obsidian']['size_mb']:>6.2f} MB)                  ║
║ Holographic Brain: {brains['holographic']['files']:>4} files  ({brains['holographic']['size_mb']:>6.2f} MB)                  ║
║ Vector Memory:     {brains['vector_chunks']:>4} chunks                                   ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ AGENT WORKFORCE ({active_agents}/{total_agents} ACTIVE)                                          ║
╠═══════════════════════════════════════════════════════════════════════════════╣
"""
    
    for name, info in agents.items():
        status_icon = "●" if info.get("status") == "active" else "○"
        report += f"║ {status_icon} {info.get('name', name):<15} ({info.get('archangel', '')}): {info.get('role', '')}\n"
    
    report += "╠═══════════════════════════════════════════════════════════════════════════════╣\n"
    report += "║ TODAY'S SCHEDULE                                                           ║\n"
    report += "╠══════════════════════════════════════════════════════════════════════════════╣\n"
    
    if appointments:
        for appt in appointments:
            report += f"║ {appt.get('time', 'TBD')} - {appt.get('title', 'Appointment')}\n"
    else:
        report += "║ No appointments scheduled (integrate Google Calendar for real data)       ║\n"
    
    report += "╠══════════════════════════════════════════════════════════════════════════════╣\n"
    report += "║ PENDING TASKS                                                              ║\n"
    report += "╠══════════════════════════════════════════════════════════════════════════════╣\n"
    
    if tasks:
        for task in tasks[:5]:
            report += f"║ □ {task.get('title', 'Task')}\n"
    else:
        report += "║ No pending tasks (integrate task queue for real data)                    ║\n"
    
    report += "╠══════════════════════════════════════════════════════════════════════════════╣\n"
    report += "║ PRIORITIES                                                                 ║\n"
    report += "╠══════════════════════════════════════════════════════════════════════════════╣\n"
    report += "║ 1. Complete J.A.R.V.I.S. dual-brain architecture                           ║\n"
    report += "║ 2. Deploy 12 archangel agents for business automation                      ║\n"
    report += "║ 3. Integrate voice pipeline (STT/TTS) with J.A.R.V.I.S. persona            ║\n"
    report += "║ 4. Automate The Great Sage Tattoos and Tarot operations                    ║\n"
    report += "║ 5. Achieve sustainable revenue from automated systems                      ║\n"
    report += "╚══════════════════════════════════════════════════════════════════════════════╝\n"
    
    return report


def main():
    report = generate_report()
    print(report)
    
    # Save to log
    log_file = LOGS_DIR / f"daily_report_{datetime.now().strftime('%Y%m%d')}.log"
    LOGS_DIR.mkdir(exist_ok=True)
    with open(log_file, "w") as f:
        f.write(report)
    
    # Also save as latest
    latest_file = LOGS_DIR / "daily_report_latest.log"
    with open(latest_file, "w") as f:
        f.write(report)
    
    print(f"\n✓ Daily report saved to {log_file}")


if __name__ == "__main__":
    main()