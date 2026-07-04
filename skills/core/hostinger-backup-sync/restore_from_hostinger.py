#!/usr/bin/env python3
"""
J.A.R.V.I.S. Hostinger Restore
Restore system from Hostinger backup.
"""

import os
import subprocess
import sys
import json
from pathlib import Path
from typing import List

JARVIS_ROOT = Path("/opt/data/jarvis")
BACKUP_DIRS = [
    "config",
    "obsidian_brain",
    "holographic_brain",
    "vector_memory",
    "skills",
    "scripts",
    "security/hashes",
    "agents",
]

class HostingerRestore:
    def __init__(self, backup_date: str = None):
        self.host = os.environ.get("HOSTINGER_HOST")
        self.user = os.environ.get("HOSTINGER_USER")
        self.remote_path = os.environ.get("HOSTINGER_PATH", "/home/user/jarvis_backups")
        self.ssh_key = os.environ.get("HOSTINGER_SSH_KEY")
        self.backup_date = backup_date
        
        if not all([self.host, self.user, self.remote_path]):
            raise ValueError("Missing required environment variables")
    
    def _run_cmd(self, cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
        print(f"$ {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr and check:
            print(f"STDERR: {result.stderr}", file=sys.stderr)
        if check and result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
        return result
    
    def _rsync_base(self) -> List[str]:
        base = ["rsync", "-avz", "--progress"]
        if self.ssh_key:
            base.extend(["-e", f"ssh -i {self.ssh_key} -o StrictHostKeyChecking=no -o BatchMode=yes"])
        return base
    
    def list_backups(self) -> List[str]:
        """List available backup dates on remote."""
        ssh_cmd = ["ssh"]
        if self.ssh_key:
            ssh_cmd.extend(["-i", self.ssh_key])
        ssh_cmd.extend([f"{self.user}@{self.host}", f"ls -1 {self.remote_path}/backups/ 2>/dev/null || echo 'no_backups_dir'"])
        result = self._run_cmd(ssh_cmd, check=False)
        if result.returncode == 0:
            return [d for d in result.stdout.strip().split('\n') if d and d != 'no_backups_dir']
        return []
    
    def restore(self, target_date: str = None) -> bool:
        """Restore from backup."""
        date = target_date or self.backup_date or "latest"
        
        if date == "latest":
            backups = self.list_backups()
            if not backups:
                print("No backups found on remote")
                return False
            date = sorted(backups)[-1]
            print(f"Using latest backup: {date}")
        
        remote_base = f"{self.user}@{self.host}:{self.remote_path}/backups/{date}/"
        
        # Restore each directory
        for backup_dir in BACKUP_DIRS:
            local = JARVIS_ROOT / backup_dir
            local.parent.mkdir(parents=True, exist_ok=True)
            
            remote = f"{remote_base}{backup_dir}/"
            cmd = self._rsync_base() + [remote, f"{local}/"]
            try:
                self._run_cmd(cmd)
                print(f"✓ Restored {backup_dir}")
            except subprocess.CalledProcessError as e:
                print(f"✗ Failed to restore {backup_dir}: {e}")
                return False
        
        print(f"✓ Restore complete from {date}")
        return True
    
    def verify_restore(self) -> bool:
        """Verify restored files against manifest."""
        manifest_path = JARVIS_ROOT / "backup_manifest.json"
        if not manifest_path.exists():
            print("No manifest found for verification")
            return False
        
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        import hashlib
        errors = 0
        for file_info in manifest["files"]:
            file_path = JARVIS_ROOT / file_info["path"]
            if not file_path.exists():
                print(f"✗ Missing: {file_info['path']}")
                errors += 1
                continue
            
            hasher = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)
            
            if hasher.hexdigest() != file_info["sha256"]:
                print(f"✗ Hash mismatch: {file_info['path']}")
                errors += 1
        
        if errors == 0:
            print("✓ Restore verification PASSED")
            return True
        else:
            print(f"✗ Restore verification FAILED: {errors} errors")
            return False


def main():
    def main():
        import argparse
        parser = argparse.ArgumentParser(description="J.A.R.V.I.S. Hostinger Restore")
        parser.add_argument("--backup-date", help="Specific backup date (YYYY-MM-DD) or 'latest'")
        parser.add_argument("--list", action="store_true", help="List available backups")
        parser.add_argument("--verify", action="store_true", help="Verify current restore")
        
        args = parser.parse_args()
        
        try:
            restore = HostingerRestore(args.backup_date)
        except ValueError as e:
            print(f"Configuration error: {e}")
            sys.exit(1)
        
        if args.list:
            backups = restore.list_backups()
            if backups:
                print("Available backups:")
                for b in sorted(backups):
                    print(f"  {b}")
            else:
                print("No backups found")
        elif args.verify:
            success = restore.verify_restore()
            sys.exit(0 if success else 1)
        else:
            success = restore.restore(args.backup_date)
            sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()