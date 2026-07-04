#!/usr/bin/env python3
"""
J.A.R.V.I.S. Nightly Audit
Code review, security scan, performance check.
"""

import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

JARVIS_ROOT = Path("/opt/data/jarvis")
LOGS_DIR = JARVIS_ROOT / "logs"
SECURITY_DIR = JARVIS_ROOT / "security"


def run_cmd(cmd: list) -> str:
    """Run command and return output."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Timeout", 1
    except Exception as e:
        return "", str(e), 1


def security_audit() -> dict:
    """Run security audit."""
    results = {}
    
    # Check file permissions
    stdout, stderr, code = run_cmd(["find", str(JARVIS_ROOT), "-type", "f", "!", "-perm", "600", "!", "-perm", "700", "!", "-path", "*/venv/*", "!", "-path", "*/.git/*"])
    results["file_permissions"] = {"issues": stdout.split('\n') if stdout else [], "count": len(stdout.split('\n')) if stdout else 0}
    
    # Check for exposed secrets
    stdout, stderr, code = run_cmd(["grep", "-r", "-i", "api_key\\|secret\\|password\\|token", str(JARVIS_ROOT), "--exclude-dir=venv", "--exclude-dir=.git", "--exclude=*.log"])
    results["secrets_scan"] = {"found": stdout.split('\n') if stdout else [], "count": len(stdout.split('\n')) if stdout else 0}
    
    # Verify integrity hashes
    hash_file = SECURITY_DIR / "hashes" / "current.json"
    if hash_file.exists():
        stdout, stderr, code = run_cmd(["python", "-c", f"""
import json, hashlib
with open('{hash_file}') as f:
    hashes = json.load(f)
errors = 0
for path, expected in hashes.items():
    try:
        with open(path, 'rb') as f:
            actual = hashlib.sha256(f.read()).hexdigest()
        if actual != expected:
            print(f'MISMATCH: {{path}}')
            errors += 1
    except:
        print(f'MISSING: {{path}}')
        errors += 1
print(f'Total errors: {{errors}}')
"""])
        results["integrity_check"] = {"output": stdout, "errors": "errors" in stdout.lower()}
    else:
        results["integrity_check"] = {"output": "No hash baseline found", "errors": True}
    
    return results


def code_audit() -> dict:
    """Run code quality audit."""
    results = {}
    
    # Python syntax check
    stdout, stderr, code = run_cmd(["find", str(JARVIS_ROOT), "-name", "*.py", "!", "-path", "*/venv/*", "-exec", "python", "-m", "py_compile", "{}", ";"])
    results["python_syntax"] = {"errors": stderr if code != 0 else "OK", "return_code": code}
    
    # Check for TODO/FIXME
    stdout, stderr, code = run_cmd(["grep", "-r", "TODO\\|FIXME\\|HACK", str(JARVIS_ROOT), "--exclude-dir=venv", "--exclude-dir=.git"])
    results["code_markers"] = {"count": len(stdout.split('\n')) if stdout else 0, "items": stdout.split('\n')[:10] if stdout else []}
    
    return results


def performance_check() -> dict:
    """Run performance checks."""
    import psutil
    
    results = {}
    
    # System resources
    cpu = psutil.cpu_percent(interval=2)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    results["system"] = {
        "cpu_percent": cpu,
        "memory_percent": memory.percent,
        "disk_percent": round(disk.used / disk.total * 100, 1)
    }
    
    # Process count
    results["process_count"] = len(psutil.pids())
    
    # Large files
    stdout, stderr, code = run_cmd(["find", str(JARVIS_ROOT), "-type", "f", "-size", "+100M", "!", "-path", "*/venv/*"])
    results["large_files"] = stdout.split('\n') if stdout else []
    
    return results


def main():
    print(f"=== J.A.R.V.I.S. NIGHTLY AUDIT - {datetime.now().isoformat()} ===\n")
    
    audit_results = {
        "timestamp": datetime.now().isoformat(),
        "security": security_audit(),
        "code": code_audit(),
        "performance": performance_check()
    }
    
    # Save detailed results
    LOGS_DIR.mkdir(exist_ok=True)
    audit_file = LOGS_DIR / f"nightly_audit_{datetime.now().strftime('%Y%m%d')}.json"
    with open(audit_file, "w") as f:
        json.dump(audit_results, f, indent=2)
    
    # Print summary
    print("SECURITY AUDIT:")
    sec = audit_results["security"]
    print(f"  File permission issues: {sec['file_permissions']['count']}")
    print(f"  Secrets found: {sec['secrets_scan']['count']}")
    print(f"  Integrity check: {'PASS' if not sec['integrity_check']['errors'] else 'FAIL'}")
    
    print("\nCODE AUDIT:")
    code = audit_results["code"]
    print(f"  Python syntax: {'OK' if code['python_syntax']['return_code'] == 0 else 'ERRORS'}")
    print(f"  TODO/FIXME markers: {code['code_markers']['count']}")
    
    print("\nPERFORMANCE:")
    perf = audit_results["performance"]
    print(f"  CPU: {perf['system']['cpu_percent']:.1f}%")
    print(f"  Memory: {perf['system']['memory_percent']:.1f}%")
    print(f"  Disk: {perf['system']['disk_percent']:.1f}%")
    print(f"  Processes: {perf['process_count']}")
    print(f"  Large files (>100MB): {len(perf['large_files'])}")
    
    # Determine overall status
    issues = (
        sec['file_permissions']['count'] +
        sec['secrets_scan']['count'] +
        (1 if sec['integrity_check']['errors'] else 0) +
        (1 if code['python_syntax']['return_code'] != 0 else 0)
    )
    
    print(f"\nOVERALL: {'PASS' if issues == 0 else f'{issues} ISSUES FOUND'}")
    print(f"\n✓ Full audit saved to {audit_file}")


if __name__ == "__main__":
    main()