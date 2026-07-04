#!/usr/bin/env python3
"""
J.A.R.V.I.S. OS - Health Check Script
Checks system health for all core services.
"""

import asyncio
import sys
from pathlib import Path

JARVIS_ROOT = Path("/opt/data/JARVIS_OS")


async def check_service(name: str, port: int = None, url: str = None) -> bool:
    """Check if a service is healthy."""
    if port:
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                return s.connect_ex(('localhost', port)) == 0
        except:
            return False

    if url:
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://localhost:{url}/health", timeout=2) as resp:
                    return resp.status == 200
        except:
            return False

    return False


async def main():
    """Run health checks."""
    print("J.A.R.V.I.S. OS Health Check")
    print("=" * 40)

    checks = [
        ("Mission Control Dashboard", 8080),
        ("Ollama", 11434),
    ]

    all_healthy = True
    for name, port in checks:
        healthy = await check_service(name, port=port)
        status = "✓ HEALTHY" if healthy else "✗ UNHEALTHY"
        print(f"  {name}: {status}")
        if not healthy:
            all_healthy = False

    # Check critical files
    critical_files = [
        JARVIS_ROOT / "config" / "soul.md",
        JARVIS_ROOT / "config" / "user.md",
        JARVIS_ROOT / "config" / "integrations.yaml",
    ]

    for f in critical_files:
        exists = f.exists()
        status = "✓" if exists else "✗"
        print(f"  Config {f.name}: {status}")
        if not exists:
            all_healthy = False

    # Check directory structure
    critical_dirs = [
        JARVIS_ROOT / "brains" / "obsidian",
        JARVIS_ROOT / "brains" / "holographic",
        JARVIS_ROOT / "vector_db",
        JARVIS_ROOT / "logs",
    ]

    for d in critical_dirs:
        exists = d.exists()
        status = "✓" if exists else "✗"
        print(f"  Directory {d.relative_to(JARVIS_ROOT)}: {status}")
        if not exists:
            all_healthy = False

    print("=" * 40)
    if all_healthy:
        print("Overall: ALL SYSTEMS OPERATIONAL")
        return 0
    else:
        print("Overall: SOME CHECKS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))