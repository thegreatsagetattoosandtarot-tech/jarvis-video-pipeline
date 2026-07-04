#!/usr/bin/env python3
"""
J.A.R.V.I.S. OS - Security Audit Script
Runs security hardening verification checks.
"""

import asyncio
import subprocess
import sys
from datetime import datetime
from pathlib import Path

JARVIS_ROOT = Path("/opt/data/JARVIS_OS")


async def run_cmd(cmd: list) -> tuple:
    """Run command and return (success, output)."""
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(JARVIS_ROOT)
        )
        stdout, stderr = await proc.communicate()
        return proc.returncode == 0, stdout.decode() + stderr.decode()
    except Exception as e:
        return False, str(e)


async def check_file_permissions() -> dict:
    """Check critical file permissions."""
    results = {}
    critical_files = [
        ("config/soul.md", 0o600),
        ("config/user.md", 0o600),
        ("config/integrations.yaml", 0o600),
        ("config/security.yaml", 0o600),
        ("config/voice.yaml", 0o600),
    ]

    for rel_path, expected_perm in critical_files:
        fp = JARVIS_ROOT / rel_path
        if fp.exists():
            actual_perm = fp.stat().st_mode & 0o777
            results[rel_path] = {
                "expected": oct(expected_perm),
                "actual": oct(actual_perm),
                "passed": actual_perm == expected_perm
            }
        else:
            results[rel_path] = {"passed": False, "error": "File not found"}

    return results


async def check_ssh_config() -> dict:
    """Check SSH security configuration."""
    results = {}

    # Check SSH keys
    ssh_dir = JARVIS_ROOT / "config" / "ssh"
    if ssh_dir.exists():
        key_files = list(ssh_dir.glob("*"))
        for key in key_files:
            if not key.name.endswith(".pub"):
                perm = key.stat().st_mode & 0o777
                results[f"ssh_key_{key.name}"] = {
                    "permission": oct(perm),
                    "passed": perm in (0o400, 0o600)
                }

    # Check SSH config if exists
    ssh_config = Path("/etc/ssh/sshd_config")
    if ssh_config.exists():
        content = ssh_config.read_text()
        checks = {
            "PasswordAuthentication no": "PasswordAuthentication no" in content,
            "PermitRootLogin no": "PermitRootLogin no" in content,
            "PubkeyAuthentication yes": "PubkeyAuthentication yes" in content,
        }
        results["sshd_config"] = checks

    return results


async def check_api_keys() -> dict:
    """Check for exposed API keys in config files."""
    results = {}
    patterns = ["api_key", "password", "secret", "token", "key"]
    config_dir = JARVIS_ROOT / "config"

    for config_file in config_dir.rglob("*.yaml"):
        if config_file.name == "integrations.yaml":
            continue  # This is expected to have placeholders
        content = config_file.read_text()
        found = []
        for pattern in patterns:
            if pattern in content.lower():
                found.append(pattern)
        if found:
            results[config_file.name] = {"potential_secrets": found, "passed": False}

    return results


async def check_network_security() -> dict:
    """Check network security settings."""
    results = {}

    # Check open ports
    success, output = await run_cmd(["ss", "-tuln"])
    if success:
        results["open_ports"] = {"output": output, "passed": True}

    # Check firewall
    success, output = await run_cmd(["ufw", "status"])
    if success:
        results["firewall"] = {"output": output, "passed": "active" in output.lower()}

    return results


async def main():
    print("=" * 60)
    print(f"J.A.R.V.I.S. OS Security Audit - {datetime.now().isoformat()}")
    print("=" * 60)

    audit = {
        "timestamp": datetime.now().isoformat(),
        "file_permissions": await check_file_permissions(),
        "ssh_config": await check_ssh_config(),
        "api_keys": await check_api_keys(),
        "network_security": await check_network_security(),
    }

    # Summary
    total = 0
    passed = 0
    for category, checks in audit.items():
        if isinstance(checks, dict):
            for check_name, result in checks.items():
                total += 1
                if isinstance(result, dict) and result.get("passed"):
                    passed += 1
                elif isinstance(result, bool) and result:
                    passed += 1

    print(f"\nSECURITY AUDIT SUMMARY")
    print(f"  Checks: {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {total - passed}")

    if passed == total:
        print("\n✓ ALL SECURITY CHECKS PASSED")
        return 0
    else:
        print("\n⚠ SOME CHECKS FAILED - REVIEW REQUIRED")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))