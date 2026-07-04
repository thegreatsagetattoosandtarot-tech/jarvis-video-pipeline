#!/usr/bin/env python3
"""
J.A.R.V.I.S. Cron Automation - Install and manage cron jobs.
"""

import os
import subprocess
import sys
from pathlib import Path

JARVIS_ROOT = Path("/opt/data/jarvis")
SCRIPTS_DIR = JARVIS_ROOT / "scripts"
SKILLS_DIR = JARVIS_ROOT / "skills"
VENV_PYTHON = JARVIS_ROOT / "venv" / "bin" / "python"
LOGS_DIR = JARVIS_ROOT / "logs"

# Cron job definitions
CRON_JOBS = [
    {
        "name": "daily_report",
        "schedule": "0 6 * * *",
        "command": f"{VENV_PYTHON} {SKILLS_DIR}/cron-automation/jobs/daily_report.py",
        "description": "Daily morning briefing"
    },
    {
        "name": "weather_summary",
        "schedule": "15 6 * * *",
        "command": f"{VENV_PYTHON} {SKILLS_DIR}/cron-automation/jobs/weather_fetcher.py",
        "description": "Weather summary"
    },
    {
        "name": "stock_report",
        "schedule": "30 9 * * 1-5",
        "command": f"{VENV_PYTHON} {SKILLS_DIR}/cron-automation/jobs/stock_reporter.py",
        "description": "Stock market report (market days)"
    },
    {
        "name": "task_summary",
        "schedule": "0 8 * * *",
        "command": f"{VENV_PYTHON} {SKILLS_DIR}/cron-automation/jobs/task_summarizer.py",
        "description": "Daily task summary"
    },
    {
        "name": "financial_report",
        "schedule": "0 18 * * *",
        "command": f"{VENV_PYTHON} {SKILLS_DIR}/cron-automation/jobs/financial_reporter.py",
        "description": "Daily financial report"
    },
    {
        "name": "nightly_audit",
        "schedule": "0 2 * * *",
        "command": f"{VENV_PYTHON} {SKILLS_DIR}/cron-automation/jobs/nightly_audit.py",
        "description": "Nightly code/security/performance audit"
    },
    {
        "name": "weekly_review",
        "schedule": "0 7 * * 1",
        "command": f"{VENV_PYTHON} {SKILLS_DIR}/cron-automation/jobs/weekly_review.py",
        "description": "Weekly review (Mondays)"
    },
    {
        "name": "monthly_review",
        "schedule": "0 8 1 * *",
        "command": f"{VENV_PYTHON} {SKILLS_DIR}/cron-automation/jobs/monthly_review.py",
        "description": "Monthly review (1st of month)"
    },
    {
        "name": "dream_process",
        "schedule": "0 3 * * *",
        "command": f"{VENV_PYTHON} {SKILLS_DIR}/cron-automation/jobs/dream_process.py",
        "description": "Nightly dream process"
    },
    {
        "name": "hostinger_backup",
        "schedule": "0 4 * * *",
        "command": f"{SCRIPTS_DIR}/backup_hostinger.sh",
        "description": "Daily Hostinger backup"
    },
    {
        "name": "vector_reindex",
        "schedule": "0 5 * * *",
        "command": f"{VENV_PYTHON} {SKILLS_DIR}/vector-memory-rag/index_brains.py",
        "description": "Daily vector memory re-index"
    },
    {
        "name": "health_check",
        "schedule": "*/15 * * * *",
        "command": f"{VENV_PYTHON} {SKILLS_DIR}/cron-automation/jobs/health_check.py",
        "description": "System health check (every 15 min)"
    },
]

def get_current_crontab():
    """Get current crontab."""
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout
    return ""

def install_cron_jobs():
    """Install all J.A.R.V.I.S. cron jobs."""
    current = get_current_crontab()
    
    # Filter out existing JARVIS jobs
    lines = current.split('\n')
    filtered = [l for l in lines if "JARVIS" not in l and l.strip()]
    
    # Add new jobs
    new_lines = filtered.copy()
    new_lines.append("# === JARVIS AUTOMATION JOBS ===")
    
    for job in CRON_JOBS:
        cron_line = f"{job['schedule']} {job['command']} >> {LOGS_DIR}/{job['name']}.log 2>&1 # JARVIS:{job['name']}"
        new_lines.append(cron_line)
    
    new_lines.append("# === END JARVIS JOBS ===")
    
    new_crontab = '\n'.join(new_lines) + '\n'
    
    # Write to temporary file and install
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.cron', delete=False) as f:
        f.write(new_crontab)
        temp_path = f.name
    
    try:
        result = subprocess.run(["crontab", temp_path], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Cron jobs installed successfully")
            for job in CRON_JOBS:
                print(f"  {job['schedule']} - {job['name']} ({job['description']})")
        else:
            print(f"✗ Failed to install cron: {result.stderr}")
    finally:
        os.unlink(temp_path)

def remove_cron_jobs():
    """Remove all JARVIS cron jobs."""
    current = get_current_crontab()
    lines = current.split('\n')
    filtered = [l for l in lines if "JARVIS" not in l]
    
    new_crontab = '\n'.join(filtered) + '\n'
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.cron', delete=False) as f:
        f.write(new_crontab)
        temp_path = f.name
    
    try:
        result = subprocess.run(["crontab", temp_path], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ JARVIS cron jobs removed")
        else:
            print(f"✗ Failed to remove cron: {result.stderr}")
    finally:
        os.unlink(temp_path)

def list_cron_jobs():
    """List current JARVIS cron jobs."""
    current = get_current_crontab()
    lines = current.split('\n')
    jarvis_jobs = [l for l in lines if "JARVIS:" in l]
    
    if jarvis_jobs:
        print("Current JARVIS cron jobs:")
        for job in jarvis_jobs:
            print(f"  {job}")
    else:
        print("No JARVIS cron jobs found")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="J.A.R.V.I.S. Cron Job Manager")
    parser.add_argument("--install", action="store_true", help="Install all cron jobs")
    parser.add_argument("--remove", action="store_true", help="Remove all JARVIS cron jobs")
    parser.add_argument("--list", action="store_true", help="List current JARVIS cron jobs")
    
    args = parser.parse_args()
    
    if args.install:
        install_cron_jobs()
    elif args.remove:
        remove_cron_jobs()
    elif args.list:
        list_cron_jobs()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()