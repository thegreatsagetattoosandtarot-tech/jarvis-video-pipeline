#!/usr/bin/env python3
"""
J.A.R.V.I.S. Hostinger Backup Sync (SCP/SFTP version)
Synchronizes J.A.R.V.I.S. system to Hostinger server via SCP over SSH.
Works without rsync - uses scp uses scp and ssh for file transfers.
"""

import argparse
import os
import subprocess
import sys
import json
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path

JARVIS_ROOT = Path("/opt/data/jarvis")
CONFIG_FILE = JARVIS_ROOT / "config" / "hostinger_backup.json"
LOGS_DIR = JARVIS_ROOT / "logs"

# Default paths to backup
BACKUP_PATHS = [
    "config",
    "obsidian_brain",
    "holographic_brain",
    "vector_memory",
    "skills",
    "scripts",
    "security",
    "dashboard",
    "voices",
]

# Paths to exclude
EXCLUDE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    ".git",
    "venv",
    ".venv",
    "node_modules",
    "*.log",
    "*.tmp",
    ".cache",
    "chroma",
    "*.onnx",
    "*.onnx.json",
]


def load_config():
    """Load Hostinger backup configuration."""
    if not CONFIG_FILE.exists():
        template = {
            "host": "your-hostinger-host.com",
            "user": "your-username",
            "path": "/home/your-username/jarvis_backups",
            "ssh_key": "/opt/data/jarvis/.ssh/hostinger_key",
            "port": 22,
            "retention_days": 30,
            "verify_after_sync": True
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(template, f, indent=2)
        print(f"Created template config at {CONFIG_FILE}")
        print("Please edit with your Hostinger credentials")
        return None

    with open(CONFIG_FILE) as f:
        return json.load(f)


def should_exclude(path: Path, root: Path) -> bool:
    """Check if path should be excluded."""
    rel = path.relative_to(root)
    rel_str = str(rel)
    
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith("*"):
            if rel_str.endswith(pattern[1:]):
                return True
        elif pattern in rel_str:
            return True
    return False


def create_backup_archive(config, incremental=False) -> Path:
    """Create a tar.gz archive of all backup paths."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"jarvis_backup_{timestamp}.tar.gz"
    archive_path = Path(tempfile.gettempdir()) / archive_name
    
    print(f"Creating archive: {archive_name}")
    
    with tarfile.open(archive_path, "w:gz") as tar:
        for path_name in BACKUP_PATHS:
            path = JARVIS_ROOT / path_name
            if not path.exists():
                print(f"  Skipping {path_name} (not found)")
                continue
            
            print(f"  Adding {path_name}...")
            for root, dirs, files in os.walk(path):
                # Filter dirs in-place
                dirs[:] = [d for d in dirs if not should_exclude(Path(root) / d, JARVIS_ROOT)]
                
                for f in files:
                    fp = Path(root) / f
                    if should_exclude(fp, JARVIS_ROOT):
                        continue
                    
                    try:
                        arcname = fp.relative_to(JARVIS_ROOT)
                        tar.add(fp, arcname=str(arcname))
                    except Exception as e:
                        print(f"    Warning: failed to add {fp}: {e}")
    
    size_mb = archive_path.stat().st_size / (1024 * 1024)
    print(f"Archive created: {archive_path} ({size_mb:.1f} MB)")
    return archive_path


def run_scp(archive_path: Path, config) -> bool:
    """Upload archive via scp."""
    ssh_key = config.get("ssh_key", "")
    port = config.get("port", 22)
    host = config["host"]
    user = config["user"]
    remote_path = config["path"]
    
    # Ensure remote directory exists
    ssh_cmd = [
        "ssh", "-p", str(port), "-i", ssh_key,
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        f"{user}@{host}",
        f"mkdir -p {remote_path}"
    ]
    
    print("Creating remote directory...")
    result = subprocess.run(ssh_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Failed to create remote dir: {result.stderr}")
        return False
    
    # Upload via scp
    remote_file = f"{user}@{host}:{remote_path}/{archive_path.name}"
    scp_cmd = [
        "scp", "-P", str(port), "-i", ssh_key,
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        str(archive_path), remote_file
    ]
    
    print(f"Uploading to {remote_file}...")
    result = subprocess.run(scp_cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Upload FAILED: {result.stderr}")
        return False
    
    print("Upload completed successfully")
    return True


def verify_backup(config) -> bool:
    """Verify backup by checking remote archive exists."""
    ssh_key = config.get("ssh_key", "")
    port = config.get("port", 22)
    host = config["host"]
    user = config["user"]
    remote_path = config["path"]
    
    ssh_cmd = [
        "ssh", "-p", str(port), "-i", ssh_key,
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        f"{user}@{host}",
        f"ls -lh {remote_path}/jarvis_backup_*.tar.gz 2>/dev/null | tail -5"
    ]
    
    print("Verifying remote backup...")
    result = subprocess.run(ssh_cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Verification failed: {result.stderr}")
        return False
    
    if result.stdout.strip():
        print("Remote backups found:")
        print(result.stdout)
        print("Verification PASSED")
        return True
    else:
        print("No backups found on remote")
        return False


def cleanup_old_backups(config):
    """Clean up old backups based on retention policy."""
    retention = config.get("retention_days", 30)
    
    ssh_key = config.get("ssh_key", "")
    port = config.get("port", 22)
    host = config["host"]
    user = config["user"]
    path = config["path"]
    
    ssh_cmd = [
        "ssh", "-p", str(port), "-i", ssh_key,
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        f"{user}@{host}",
        f"find {path} -name 'jarvis_backup_*.tar.gz' -mtime +{retention} -delete"
    ]
    
    result = subprocess.run(ssh_cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Cleaned up backups older than {retention} days")
    else:
        print(f"Cleanup warning: {result.stderr}")


def main():
    parser = argparse.ArgumentParser(description="J.A.R.V.I.S. Hostinger Backup Sync (SCP)")
    parser.add_argument("--full", action="store_true", help="Full backup (default)")
    parser.add_argument("--incremental", action="store_true", help="Incremental (same as full for now)")
    parser.add_argument("--verify", action="store_true", help="Verify backup integrity")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (create archive only, no upload)")
    parser.add_argument("--cleanup", action="store_true", help="Cleanup old backups")
    
    args = parser.parse_args()
    
    config = load_config()
    if not config:
        return 1
    
    if args.verify:
        return 0 if verify_backup(config) else 1
    
    if args.cleanup:
        cleanup_old_backups(config)
        return 0
    
    # Create archive
    archive_path = create_backup_archive(config, incremental=args.incremental)
    
    if args.dry_run:
        print(f"Dry run complete. Archive at: {archive_path}")
        print("Not uploading (--dry-run specified)")
        return 0
    
    # Upload
    success = run_scp(archive_path, config)
    
    # Cleanup local archive
    try:
        archive_path.unlink()
        print("Local archive cleaned up")
    except:
        pass
    
    if success and config.get("verify_after_sync", True):
        print("\nRunning post-backup verification...")
        verify_backup(config)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())