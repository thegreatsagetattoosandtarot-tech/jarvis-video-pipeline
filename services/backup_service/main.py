#!/usr/bin/env python3
"""
J.A.R.V.I.S. OS - Backup Service
Automated backup synchronization to Hostinger server.
"""

import asyncio
import json
import os
import subprocess
import tempfile
import tarfile
from datetime import datetime
from pathlib import Path
from typing import Optional

JARVIS_ROOT = Path("/opt/data/JARVIS_OS")
CONFIG_FILE = JARVIS_ROOT / "config" / "integrations.yaml"

BACKUP_PATHS = [
    "config",
    "brains/obsidian",
    "brains/holographic",
    "vector_db",
    "skills",
    "scripts",
    "agents",
]

EXCLUDE_PATTERNS = [
    "__pycache__", "*.pyc", ".git", "venv", ".venv",
    "node_modules", "*.log", "*.tmp", ".cache",
    "chroma", "*.onnx", "*.onnx.json"
]


def should_exclude(path: Path) -> bool:
    """Check if path should be excluded."""
    rel_str = str(path)
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith("*"):
            if rel_str.endswith(pattern[1:]):
                return True
        elif pattern in rel_str:
            return True
    return False


def load_config() -> Optional[dict]:
    """Load backup configuration from environment/integrations."""
    host = os.environ.get("HOSTINGER_HOST")
    user = os.environ.get("HOSTINGER_USER")
    path = os.environ.get("HOSTINGER_PATH", "/home/user/jarvis_backups")
    ssh_key = os.environ.get("HOSTINGER_SSH_KEY", "/opt/data/JARVIS_OS/config/ssh/hostinger_key")
    port = int(os.environ.get("HOSTINGER_PORT", "22"))

    if not all([host, user]):
        print("Missing HOSTINGER_HOST or HOSTINGER_USER environment variables")
        return None

    return {
        "host": host,
        "user": user,
        "path": path,
        "ssh_key": ssh_key,
        "port": port
    }


def create_archive() -> Path:
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
                dirs[:] = [d for d in dirs if not should_exclude(Path(root) / d)]

                for f in files:
                    fp = Path(root) / f
                    if should_exclude(fp):
                        continue
                    try:
                        arcname = fp.relative_to(JARVIS_ROOT)
                        tar.add(fp, arcname=str(arcname))
                    except Exception as e:
                        print(f"    Warning: failed to add {fp}: {e}")

    size_mb = archive_path.stat().st_size / (1024 * 1024)
    print(f"Archive created: {archive_path} ({size_mb:.1f} MB)")
    return archive_path


def upload_archive(archive_path: Path, config: dict) -> bool:
    """Upload archive via SCP."""
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


def verify_backup(config: dict) -> bool:
    """Verify backup exists on remote."""
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


def cleanup_old_backups(config: dict, retention_days: int = 30):
    """Clean up old backups based on retention policy."""
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
        f"find {path} -name 'jarvis_backup_*.tar.gz' -mtime +{retention_days} -delete"
    ]

    result = subprocess.run(ssh_cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Cleaned up backups older than {retention_days} days")
    else:
        print(f"Cleanup warning: {result.stderr}")


async def run_backup(incremental: bool = False) -> bool:
    """Run a backup operation."""
    print("=" * 60)
    print(f"J.A.R.V.I.S. OS Backup - {datetime.now().isoformat()}")
    print("=" * 60)

    config = load_config()
    if not config:
        return False

    # Create archive
    archive_path = create_archive()

    # Upload
    success = upload_archive(archive_path, config)

    # Cleanup local archive
    try:
        archive_path.unlink()
        print("Local archive cleaned up")
    except:
        pass

    # Verify
    if success:
        verify_backup(config)
        cleanup_old_backups(config)

    return success


async def main():
    """Main backup service loop."""
    import argparse
    parser = argparse.ArgumentParser(description="J.A.R.V.I.S. OS Backup Service")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--incremental", action="store_true", help="Incremental backup")
    parser.add_argument("--verify", action="store_true", help="Verify only")
    parser.add_argument("--cleanup", action="store_true", help="Cleanup old backups only")
    args = parser.parse_args()

    config = load_config()
    if not config:
        return 1

    if args.verify:
        return 0 if verify_backup(config) else 1

    if args.cleanup:
        cleanup_old_backups(config)
        return 0

    if args.once:
        return 0 if await run_backup(args.incremental) else 1

    # Run as service - daily at 4 AM
    print("Backup service running. Will backup daily at 4:00 AM")
    while True:
        now = datetime.now()
        # Next 4 AM
        next_run = now.replace(hour=4, minute=0, second=0, microsecond=0)
        if next_run <= now:
            from datetime import timedelta
            next_run += timedelta(days=1)

        wait_seconds = (next_run - now).total_seconds()
        print(f"Next backup at {next_run} ({wait_seconds/3600:.1f} hours)")

        await asyncio.sleep(wait_seconds)
        await run_backup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBackup service stopped")