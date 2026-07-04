#!/usr/bin/env python3
"""
J.A.R.V.I.S. Health Check
Runs every 15 minutes to monitor system health.
"""

import json
import psutil
from datetime import datetime
from pathlib import Path

JARVIS_ROOT = Path("/opt/data/jarvis")
LOGS_DIR = JARVIS_ROOT / "logs"


def check_health() -> dict:
    """Check system health and return metrics."""
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": cpu,
        "memory_percent": memory.percent,
        "disk_percent": round(disk.used / disk.total * 100, 1),
        "status": "HEALTHY" if cpu < 90 and memory.percent < 90 and disk.percent < 90 else "WARNING"
    }


def main():
    health = check_health()
    
    # Log to file
    LOGS_DIR.mkdir(exist_ok=True)
    log_file = LOGS_DIR / "health_check.jsonl"
    
    with open(log_file, "a") as f:
        f.write(json.dumps(health) + "\n")
    
    # Alert if unhealthy
    if health["status"] != "HEALTHY":
        alert_file = LOGS_DIR / "health_alerts.log"
        with open(alert_file, "a") as f:
            f.write(f"{health['timestamp']} - {health}\n")


if __name__ == "__main__":
    main()