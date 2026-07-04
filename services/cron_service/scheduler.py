#!/usr/bin/env python3
"""
J.A.R.V.I.S. OS - Cron Automation Service
Runs scheduled jobs based on cron_jobs.yaml configuration.
"""

import asyncio
import json
import os
import sys
import subprocess
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import croniter

JARVIS_ROOT = Path("/opt/data/JARVIS_OS")
CONFIG_DIR = JARVIS_ROOT / "config"
CRON_CONFIG = CONFIG_DIR / "cron_jobs.yaml"
LOGS_DIR = JARVIS_ROOT / "logs"


class CronJob:
    """Represents a single cron job."""

    def __init__(self, config: Dict[str, Any]):
        self.name = config.get("name", "")
        self.schedule = config.get("schedule", "")
        self.service = config.get("service", "")
        self.action = config.get("action", "")
        self.enabled = config.get("enabled", True)
        self.description = config.get("description", "")
        self.timeout = config.get("timeout", 300)
        self.retries = config.get("retries", 2)
        self.params = config.get("params", {})

        # Calculate next run
        self.next_run = self._calculate_next_run()

    def _calculate_next_run(self) -> datetime:
        """Calculate next run time from cron schedule."""
        try:
            cron = croniter.croniter(self.schedule, datetime.now())
            return cron.get_next(datetime)
        except Exception as e:
            print(f"Error parsing cron schedule '{self.schedule}': {e}")
            return datetime.max


class CronService:
    """Cron automation service for J.A.R.V.I.S. OS."""

    def __init__(self):
        self.jobs: List[CronJob] = []
        self.running = False
        self._task = None
        self.load_config()

    def load_config(self):
        """Load cron jobs from YAML configuration."""
        if not CRON_CONFIG.exists():
            print(f"Cron config not found: {CRON_CONFIG}")
            return

        try:
            with open(CRON_CONFIG) as f:
                data = yaml.safe_load(f)

            jobs_config = data.get("jobs", [])
            execution = data.get("execution", {})

            self.max_concurrent = execution.get("max_concurrent_jobs", 3)
            self.default_timeout = execution.get("default_timeout", 300)
            self.default_retries = execution.get("default_retries", 2)
            self.retry_delay = execution.get("retry_delay", 60)

            for job_config in jobs_config:
                if job_config.get("enabled", True):
                    job = CronJob(job_config)
                    self.jobs.append(job)

            print(f"Loaded {len(self.jobs)} cron jobs")

        except Exception as e:
            print(f"Failed to load cron config: {e}")

    def get_due_jobs(self) -> List[CronJob]:
        """Get jobs that are due to run."""
        now = datetime.now()
        return [job for job in self.jobs if job.next_run <= now and job.enabled]

    async def run_job(self, job: CronJob) -> bool:
        """Execute a single cron job."""
        print(f"Running job: {job.name} ({job.description})")

        # Build command based on service and action
        cmd = self._build_command(job)
        if not cmd:
            print(f"  No command for service '{job.service}' action '{job.action}'")
            return False

        for attempt in range(job.retries + 1):
            try:
                print(f"  Attempt {attempt + 1}/{job.retries + 1}")

                result = await asyncio.wait_for(
                    asyncio.create_subprocess_exec(
                        *cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=str(JARVIS_ROOT)
                    ),
                    timeout=job.timeout
                )

                stdout, stderr = await result.communicate()

                if result.returncode == 0:
                    print(f"  ✓ Job completed successfully")
                    return True
                else:
                    error_msg = stderr.decode() if stderr else "Unknown error"
                    print(f"  ✗ Job failed: {error_msg}")

            except asyncio.TimeoutError:
                print(f"  ✗ Job timed out after {job.timeout}s")
            except Exception as e:
                print(f"  ✗ Job error: {e}")

            if attempt < job.retries:
                print(f"  Retrying in {self.retry_delay}s...")
                await asyncio.sleep(self.retry_delay)

        return False

    def _build_command(self, job: CronJob) -> Optional[List[str]]:
        """Build command for job based on service and action."""
        # Map services to commands
        service_commands = {
            "cron_service": {
                "health_check": ["python3", "-m", "services.cron_service.health_check"],
                "check_services": ["python3", "-m", "services.cron_service.check_services"],
                "generate_daily_report": ["python3", "-m", "scripts.daily_report"],
                "fetch_weather": ["python3", "-m", "scripts.weather"],
                "fetch_stocks": ["python3", "-m", "scripts.stocks"],
                "summarize_tasks": ["python3", "-m", "scripts.task_summary"],
                "generate_financial_report": ["python3", "-m", "scripts.financial_report"],
                "run_nightly_audit": ["python3", "-m", "scripts.nightly_audit"],
                "sync_brains": ["python3", "-m", "scripts.brain_sync.sync_brains"],
                "reindex_vector_db": ["python3", "-m", "scripts.brain_sync.reindex"],
                "run_dream_process": ["python3", "-m", "scripts.dream_process"],
                "rotate_logs": ["python3", "-m", "scripts.log_rotate"],
                "verify_integrity": ["python3", "-m", "scripts.integrity_check"],
                "security_audit": ["python3", "-m", "scripts.security_audit"],
                "check_updates": ["python3", "-m", "scripts.update_check"],
            },
            "brain_sync": {
                "sync_brains": ["python3", "-m", "services.brain_sync.brain_sync_service", "--once"],
                "reindex_vector_db": ["python3", "-m", "services.brain_sync.brain_sync_service", "--reindex"],
            },
            "backup_service": {
                "sync_to_hostinger": ["python3", "-m", "services.backup_service.main", "--once"],
            },
            "agent_orchestrator": {
                "check_agent_health": ["python3", "-m", "core.agent_orchestrator", "--health-check"],
            },
        }

        service_map = service_commands.get(job.service, {})
        base_cmd = service_map.get(job.action)

        if not base_cmd:
            # Try to construct generic command
            script_path = JARVIS_ROOT / "scripts" / f"{job.action}.py"
            if script_path.exists():
                base_cmd = ["python3", str(script_path)]
            else:
                return None

        # Add parameters
        cmd = base_cmd.copy()
        for key, value in job.params.items():
            cmd.append(f"--{key}")
            cmd.append(str(value))

        return cmd

    def _update_job_next_run(self, job: CronJob):
        """Update job's next run time."""
        try:
            cron = croniter.croniter(job.schedule, datetime.now())
            job.next_run = cron.get_next(datetime)
        except Exception as e:
            print(f"Error updating next run for {job.name}: {e}")

    async def scheduler_loop(self):
        """Main scheduler loop."""
        print("Cron scheduler started")
        self.running = True

        while self.running:
            try:
                now = datetime.now()
                due_jobs = self.get_due_jobs()

                for job in due_jobs:
                    # Check concurrent limit
                    running_count = sum(1 for j in self.jobs if hasattr(j, '_running') and j._running)
                    if running_count >= self.max_concurrent:
                        print(f"Max concurrent jobs reached, skipping {job.name}")
                        continue

                    # Run job
                    job._running = True
                    success = await self.run_job(job)
                    job._running = False

                    # Update next run
                    self._update_job_next_run(job)

                    # Log result
                    log_entry = {
                        "timestamp": datetime.now().isoformat(),
                        "job": job.name,
                        "success": success,
                        "next_run": job.next_run.isoformat()
                    }
                    self._log_job(log_entry)

            except Exception as e:
                print(f"Scheduler loop error: {e}")

            # Check every 30 seconds
            await asyncio.sleep(30)

    def _log_job(self, entry: Dict):
        """Log job execution."""
        log_file = LOGS_DIR / "cron" / "cron_jobs.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            print(f"Failed to log job: {e}")

    async def start(self):
        """Start the cron service."""
        if not self.jobs:
            print("No jobs configured")
            return

        print("Starting J.A.R.V.I.S. Cron Service...")
        self._task = asyncio.create_task(self.scheduler_loop())
        await self._task

    async def stop(self):
        """Stop the cron service."""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        print("Cron service stopped")


async def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="J.A.R.V.I.S. Cron Service")
    parser.add_argument("--run-once", help="Run specific job once by name")
    parser.add_argument("--list", action="store_true", help="List all jobs")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")

    args = parser.parse_args()

    service = CronService()

    if args.list:
        print("Configured Jobs:")
        for job in service.jobs:
            print(f"  {job.name}: {job.schedule} - {job.description}")
            print(f"    Next run: {job.next_run}")
        return

    if args.run_once:
        job = next((j for j in service.jobs if j.name == args.run_once), None)
        if job:
            success = await service.run_job(job)
            print(f"Job {'succeeded' if success else 'failed'}")
        else:
            print(f"Job not found: {args.run_once}")
        return

    if args.daemon:
        await service.start()
    else:
        # Default: run once then exit
        print("Running all due jobs once...")
        due = service.get_due_jobs()
        for job in due:
            await service.run_job(job)
            service._update_job_next_run(job)


if __name__ == "__main__":
    asyncio.run(main())