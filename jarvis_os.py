#!/usr/bin/env python3
"""
J.A.R.V.I.S. OS - Main Entry Point & Service Manager
Unified launcher for all J.A.R.V.I.S. system components.
"""

import asyncio
import argparse
import json
import os
import signal
import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import psutil

JARVIS_ROOT = Path("/opt/data/JARVIS_OS")
CONFIG_DIR = JARVIS_ROOT / "config"
SERVICES_DIR = JARVIS_ROOT / "services"
LOGS_DIR = JARVIS_ROOT / "logs"
SCRIPTS_DIR = JARVIS_ROOT / "scripts"

class ServiceManager:
    """Manages all J.A.R.V.I.S. OS services."""

    def __init__(self):
        self.services: Dict[str, Any] = {}
        self.processes: Dict[str, subprocess.Popen] = {}
        self.running = False

    def load_service_config(self) -> Dict:
        """Load service configuration from YAML/JSON."""
        # Default service definitions
        return {
            "core": {
                "jarvis_daemon": {
                    "enabled": True,
                    "command": ["python3", "-m", "core.jarvis_core"],
                    "cwd": str(JARVIS_ROOT),
                    "description": "Main JARVIS daemon"
                }
            },
            "brains": {
                "brain_sync": {
                    "enabled": True,
                    "command": ["python3", str(SERVICES_DIR / "brain_sync" / "brain_sync_service.py")],
                    "cwd": str(JARVIS_ROOT),
                    "description": "Dual-brain synchronization service"
                }
            },
            "dashboard": {
                "mission_control": {
                    "enabled": True,
                    "command": ["python3", "-m", "services.mission_control.main"],
                    "cwd": str(JARVIS_ROOT),
                    "port": 8080,
                    "description": "Mission Control Dashboard (FastAPI)"
                }
            },
            "voice": {
                "voice_pipeline": {
                    "enabled": True,
                    "command": ["python3", "-m", "services.voice_service.main"],
                    "cwd": str(JARVIS_ROOT),
                    "description": "Voice pipeline (STT/TTS/Wake/RVC)"
                }
            },
            "agents": {
                "agent_orchestrator": {
                    "enabled": True,
                    "command": ["python3", "-m", "core.agent_orchestrator"],
                    "cwd": str(JARVIS_ROOT),
                    "description": "Agent orchestration service"
                }
            },
            "cron": {
                "cron_service": {
                    "enabled": True,
                    "command": ["python3", "-m", "services.cron_service.scheduler"],
                    "cwd": str(JARVIS_ROOT),
                    "description": "Scheduled automation jobs"
                }
            },
            "backup": {
                "backup_service": {
                    "enabled": True,
                    "command": ["python3", "-m", "services.backup_service.backup_scheduler"],
                    "cwd": str(JARVIS_ROOT),
                    "description": "Hostinger backup synchronization"
                }
            },
            "integration": {
                "integration_service": {
                    "enabled": False,
                    "command": ["python3", "-m", "services.integration_service.main"],
                    "cwd": str(JARVIS_ROOT),
                    "description": "External API integrations"
                }
            }
        }

    def start_service(self, category: str, service_name: str, config: Dict) -> bool:
        """Start a single service."""
        if service_name in self.processes:
            print(f"Service {service_name} already running")
            return True

        cmd = config.get("command", [])
        cwd = config.get("cwd", str(JARVIS_ROOT))

        try:
            # Prepare log file
            log_file = LOGS_DIR / f"{service_name}.log"
            log_file.parent.mkdir(parents=True, exist_ok=True)

            with open(log_file, "a") as log:
                log.write(f"\n=== Starting {service_name} at {datetime.now().isoformat()} ===\n")

            process = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            self.processes[service_name] = {
                "process": process,
                "config": config,
                "category": category,
                "started_at": datetime.now().isoformat(),
                "log_file": str(log_file)
            }

            # Start log reader
            asyncio.create_task(self._read_logs(service_name))

            print(f"✓ Started {service_name} (PID: {process.pid})")
            return True

        except Exception as e:
            print(f"✗ Failed to start {service_name}: {e}")
            return False

    async def _read_logs(self, service_name: str):
        """Read and forward service logs."""
        if service_name not in self.processes:
            return

        proc_info = self.processes[service_name]
        process = proc_info["process"]
        log_file = proc_info["log_file"]

        try:
            with open(log_file, "a") as log:
                while True:
                    line = process.stdout.readline()
                    if not line:
                        break
                    log.write(line)
                    log.flush()
        except Exception as e:
            print(f"Log reader error for {service_name}: {e}")

    def stop_service(self, service_name: str) -> bool:
        """Stop a single service."""
        if service_name not in self.processes:
            print(f"Service {service_name} not running")
            return True

        proc_info = self.processes[service_name]
        process = proc_info["process"]

        try:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

            print(f"✓ Stopped {service_name}")
            del self.processes[service_name]
            return True

        except Exception as e:
            print(f"✗ Failed to stop {service_name}: {e}")
            return False

    def get_status(self) -> Dict:
        """Get status of all services."""
        status = {}
        for name, info in self.processes.items():
            process = info["process"]
            status[name] = {
                "category": info["category"],
                "running": process.poll() is None,
                "pid": process.pid,
                "started_at": info["started_at"],
                "description": info["config"].get("description", "")
            }
        return status

    async def start_all(self, categories: Optional[List[str]] = None):
        """Start all enabled services."""
        config = self.load_service_config()

        for category, services in config.items():
            if categories and category not in categories:
                continue

            for service_name, service_config in services.items():
                if service_config.get("enabled", False):
                    self.start_service(category, service_name, service_config)
                    await asyncio.sleep(0.5)  # Stagger starts

    def stop_all(self):
        """Stop all running services."""
        for service_name in list(self.processes.keys()):
            self.stop_service(service_name)

    def check_health(self) -> Dict:
        """Check health of all services."""
        health = {}
        for name, info in self.processes.items():
            process = info["process"]
            is_running = process.poll() is None

            # Check specific health endpoints if defined
            port = info["config"].get("port")
            http_healthy = None
            if port:
                try:
                    import requests
                    resp = requests.get(f"http://localhost:{port}/health", timeout=2)
                    http_healthy = resp.status_code == 200
                except:
                    http_healthy = False

            health[name] = {
                "process_running": is_running,
                "http_healthy": http_healthy,
                "pid": process.pid if is_running else None
            }

        return health


class JARVIS_OS:
    """Main J.A.R.V.I.S. OS class."""

    def __init__(self):
        self.service_manager = ServiceManager()
        self.config = self.load_config()

    def load_config(self) -> Dict:
        """Load JARVIS OS configuration."""
        config_files = {
            "soul": CONFIG_DIR / "soul.md",
            "identity": CONFIG_DIR / "identity.md",
            "user": CONFIG_DIR / "user.md",
            "agent": CONFIG_DIR / "agent.md",
            "tools": CONFIG_DIR / "tools.md",
            "heartbeat": CONFIG_DIR / "heartbeat.md",
            "continuity": CONFIG_DIR / "continuity.md",
            "integrations": CONFIG_DIR / "integrations.yaml",
            "cron_jobs": CONFIG_DIR / "cron_jobs.yaml",
            "dashboard": CONFIG_DIR / "dashboard.yaml",
            "voice": CONFIG_DIR / "voice.yaml",
            "security": CONFIG_DIR / "security.yaml"
        }

        config = {}
        for key, path in config_files.items():
            if path.exists():
                config[key] = str(path)
            else:
                config[key] = None

        return config

    def print_banner(self):
        """Print JARVIS OS banner."""
        print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    ██╗ ██████╗  █████╗ ███╗   ██╗██╗ ██████╗ ██████╗ ███████╗ ║
║    ██║██╔════╝ ██╔══██╗████╗  ██║██║██╔═══██╗██╔══██╗██╔════╝ ║
║    ██║██║  ███╗███████║██╔██╗ ██║██║██║   ██║██║  ██║███████╗ ║
║    ██║██║   ██║██╔══██║██║╚██╗██║██║██║   ██║██║  ██║╚════██║ ║
║    ██║╚██████╔╝██║  ██║██║ ╚████║██║╚██████╔╝██████╔╝███████║ ║
║    ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝ ╚═════╝ ╚═════╝ ╚══════╝ ║
║                                                              ║
║         JUST A RATHER VERY INTELLIGENT SYSTEM               ║
║                     UNIFIED OS v1.0                         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """)

    async def initialize(self):
        """Initialize JARVIS OS."""
        self.print_banner()
        print("Initializing J.A.R.V.I.S. OS...")
        print(f"Root: {JARVIS_ROOT}")
        print(f"Config: {CONFIG_DIR}")
        print(f"Logs: {LOGS_DIR}")

        # Verify critical directories
        for dir_path in [CONFIG_DIR, LOGS_DIR, SERVICES_DIR, SCRIPTS_DIR]:
            if not dir_path.exists():
                print(f"WARNING: Missing directory: {dir_path}")

        # Load and verify config
        missing = [k for k, v in self.config.items() if v is None]
        if missing:
            print(f"WARNING: Missing config files: {', '.join(missing)}")

        print("Initialization complete\n")

    async def start(self, categories: Optional[List[str]] = None):
        """Start JARVIS OS services."""
        await self.initialize()
        print("Starting J.A.R.V.I.S. OS services...")
        await self.service_manager.start_all(categories)
        print("\nAll services started. Press Ctrl+C to stop.")

        # Keep running
        try:
            while True:
                await asyncio.sleep(60)
                # Periodic health check
                health = self.service_manager.check_health()
                unhealthy = [name for name, h in health.items() if not h["process_running"]]
                if unhealthy:
                    print(f"WARNING: Unhealthy services: {', '.join(unhealthy)}")
        except KeyboardInterrupt:
            print("\nShutdown signal received...")
            await self.shutdown()

    async def shutdown(self):
        """Graceful shutdown."""
        print("Shutting down J.A.R.V.I.S. OS...")
        self.service_manager.stop_all()
        print("Shutdown complete.")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="J.A.R.V.I.S. OS - Unified AI Operating System")
    parser.add_argument("command", choices=["start", "stop", "restart", "status", "health", "init"],
                        help="Command to execute")
    parser.add_argument("--categories", nargs="+",
                        choices=["core", "brains", "dashboard", "voice", "agents", "cron", "backup", "integration"],
                        help="Service categories to start/stop")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")

    args = parser.parse_args()

    jarvis = JARVIS_OS()

    if args.command == "init":
        await jarvis.initialize()
        print("J.A.R.V.I.S. OS initialized successfully")

    elif args.command == "start":
        await jarvis.start(args.categories)

    elif args.command == "stop":
        jarvis.service_manager.stop_all()
        print("All services stopped")

    elif args.command == "restart":
        jarvis.service_manager.stop_all()
        await asyncio.sleep(2)
        await jarvis.start(args.categories)

    elif args.command == "status":
        await jarvis.initialize()
        status = jarvis.service_manager.get_status()
        print("\nService Status:")
        print("=" * 80)
        for name, info in status.items():
            state = "● RUNNING" if info["running"] else "○ STOPPED"
            print(f"  {state}  {name:25s} (PID: {info['pid'] or 'N/A':>6s}) - {info['description']}")

    elif args.command == "health":
        await jarvis.initialize()
        health = jarvis.service_manager.check_health()
        print("\nService Health:")
        print("=" * 80)
        for name, h in health.items():
            proc = "✓" if h["process_running"] else "✗"
            http = "✓" if h["http_healthy"] else ("✗" if h["http_healthy"] is not None else "—")
            print(f"  {name:25s} Process: {proc}  HTTP: {http}  PID: {h['pid'] or 'N/A':>6s}")


if __name__ == "__main__":
    # Ensure we're in the right directory
    os.chdir(JARVIS_ROOT)
    asyncio.run(main())