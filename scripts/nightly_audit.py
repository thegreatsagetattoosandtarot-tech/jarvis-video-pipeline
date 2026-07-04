#!/usr/bin/env python3
"""
J.A.R.V.I.S. OS - Nightly Audit Script
Code review, security scan, performance check, dependency audit.
"""

import asyncio
import subprocess
import sys
from datetime import datetime
from pathlib import Path

JARVIS_ROOT = Path("/opt/data/JARVIS_OS")


async def run_command(cmd: list, timeout: int = 120) -> tuple:
    """Run a command and return (success, output)."""
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(JARVIS_ROOT)
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return proc.returncode == 0, stdout.decode() + stderr.decode()
    except asyncio.TimeoutError:
        return False, f"Command timed out after {timeout}s"
    except Exception as e:
        return False, str(e)


async def code_review() -> dict:
    """Run code quality checks."""
    results = {}

    # Python linting
    success, output = await run_command(["python3", "-m", "py_compile", "core", "services", "scripts"])
    results["python_syntax"] = {"passed": success, "output": output}

    # Check for common issues
    success, output = await run_command(["grep", "-r", "TODO\\|FIXME\\|XXX", "--include=*.py", "core", "services", "scripts"])
    results["todos"] = {"passed": not success, "output": output}  # grep returns 1 if no matches

    return results


async def security_scan() -> dict:
    """Run security checks."""
    results = {}

    # Check for hardcoded secrets
    success, output = await run_command([
        "grep", "-r", "api_key\\|password\\|secret\\|token",
        "--include=*.py", "--include=*.yaml", "--include=*.json",
        "config", "core", "services", "scripts"
    ])
    results["hardcoded_secrets"] = {"passed": not success, "output": output}

    # Check file permissions
    success, output = await run_command([
        "find", str(JARVIS_ROOT), "-type", "f",
        "(", "-name", "*.key", "-o", "-name", "*.pem", "-o", "-name", "*.secret", ")",
        "-not", "-perm", "400", "-not", "-perm", "600"
    ])
    results["key_permissions"] = {"passed": not success, "output": output}

    return results


async def performance_check() -> dict:
    """Run performance checks."""
    import psutil
    results = {}

    # System resources
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    results["cpu_percent"] = {"value": cpu, "healthy": cpu < 80}
    results["memory_percent"] = {"value": mem.percent, "healthy": mem.percent < 85}
    results["disk_percent"] = {"value": (disk.used / disk.total) * 100, "healthy": (disk.used / disk.total) * 100 < 90}

    return results


async def dependency_audit() -> dict:
    """Check for outdated dependencies."""
    results = {}

    # Check pip packages
    success, output = await run_command(["pip", "list", "--outdated", "--format=json"])
    if success:
        try:
            outdated = eval(output)
            results["pip_outdated"] = {
                "count": len(outdated),
                "packages": [f"{p['name']} ({p['version']} -> {p['latest_version']})" for p in outdated[:10]]
            }
        except:
            results["pip_outdated"] = {"count": 0, "packages": []}
    else:
        results["pip_outdated"] = {"count": 0, "packages": []}

    return results


async def main():
    """Run full nightly audit."""
    print("=" * 60)
    print(f"J.A.R.V.I.S. OS Nightly Audit - {datetime.now().isoformat()}")
    print("=" * 60)

    audit_results = {
        "timestamp": datetime.now().isoformat(),
        "code_review": await code_review(),
        "security_scan": await security_scan(),
        "performance_check": await performance_check(),
        "dependency_audit": await dependency_audit(),
    }

    # Print summary
    print("\nCODE REVIEW:")
    for check, result in audit_results["code_review"].items():
        status = "✓ PASS" if result["passed"] else "✗ FAIL"
        print(f"  {check}: {status}")

    print("\nSECURITY SCAN:")
    for check, result in audit_results["security_scan"].items():
        status = "✓ PASS" if result["passed"] else "✗ FAIL"
        print(f"  {check}: {status}")

    print("\nPERFORMANCE:")
    for check, result in audit_results["performance_check"].items():
        status = "✓ OK" if result["healthy"] else "⚠ WARNING"
        print(f"  {check}: {result['value']:.1f}% {status}")

    print("\nDEPENDENCIES:")
    dep = audit_results["dependency_audit"].get("pip_outdated", {})
    print(f"  Outdated packages: {dep.get('count', 0)}")

    # Save audit log
    log_dir = JARVIS_ROOT / "logs" / "audits"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.json"
    import json
    log_file.write_text(json.dumps(audit_results, indent=2))

    # Overall status
    all_passed = all(
        result.get("passed", True)
        for category in ["code_review", "security_scan"]
        for result in audit_results[category].values()
    )
    all_perf_ok = all(
        result.get("healthy", True)
        for result in audit_results["performance_check"].values()
    )

    print("\n" + "=" * 60)
    if all_passed and all_perf_ok:
        print("AUDIT RESULT: ALL CHECKS PASSED")
        return 0
    else:
        print("AUDIT RESULT: SOME CHECKS FAILED - REVIEW REQUIRED")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))