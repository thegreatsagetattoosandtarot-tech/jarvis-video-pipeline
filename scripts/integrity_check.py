#!/usr/bin/env python3
"""
J.A.R.V.I.S. OS - Integrity Check Script
Verifies file integrity using SHA256 hashes.
"""

import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

JARVIS_ROOT = Path("/opt/data/JARVIS_OS")
CONFIG_DIR = JARVIS_ROOT / "config"
SECURITY_DIR = JARVIS_ROOT / "config" / "security"
BASELINE_FILE = SECURITY_DIR / "integrity_baseline.json"
RESULTS_DIR = JARVIS_ROOT / "logs" / "integrity"

MONITORED_PATHS = [
    "core",
    "config",
    "scripts",
    "services",
]

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


def calculate_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of a file."""
    hasher = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        return f"ERROR: {e}"


def create_baseline() -> Dict[str, Any]:
    """Create integrity baseline of all monitored files."""
    print("Creating integrity baseline...")

    baseline = {
        "created": datetime.now().isoformat(),
        "files": {}
    }

    total_files = 0
    for path_name in MONITORED_PATHS:
        path = JARVIS_ROOT / path_name
        if not path.exists():
            continue

        for root, dirs, files in os.walk(path):
            # Filter dirs
            dirs[:] = [d for d in dirs if not should_exclude(Path(root) / d)]

            for f in files:
                fp = Path(root) / f
                if should_exclude(fp):
                    continue

                try:
                    rel_path = fp.relative_to(JARVIS_ROOT)
                    hash_val = calculate_hash(fp)
                    baseline["files"][str(rel_path)] = {
                        "hash": hash_val,
                        "size": fp.stat().st_size,
                        "modified": datetime.fromtimestamp(fp.stat().st_mtime).isoformat()
                    }
                    total_files += 1
                except Exception as e:
                    print(f"Error processing {fp}: {e}")

    print(f"Baseline created with {total_files} files")
    return baseline


def verify_integrity(baseline: Dict[str, Any]) -> Dict[str, Any]:
    """Verify current files against baseline."""
    print("Verifying integrity...")

    results = {
        "verified": datetime.now().isoformat(),
        "total_checked": 0,
        "passed": 0,
        "failed": 0,
        "missing": 0,
        "new_files": 0,
        "errors": 0,
        "details": []
    }

    baseline_files = baseline.get("files", {})

    # Check each file in baseline
    for rel_path, expected in baseline_files.items():
        fp = JARVIS_ROOT / rel_path
        results["total_checked"] += 1

        if not fp.exists():
            results["missing"] += 1
            results["details"].append({
                "file": rel_path,
                "status": "MISSING",
                "expected_hash": expected.get("hash")
            })
            continue

        try:
            actual_hash = calculate_hash(fp)
            if actual_hash == expected["hash"]:
                results["passed"] += 1
                results["details"].append({
                    "file": rel_path,
                    "status": "OK"
                })
            else:
                results["failed"] += 1
                results["details"].append({
                    "file": rel_path,
                    "status": "MODIFIED",
                    "expected_hash": expected["hash"],
                    "actual_hash": actual_hash
                })
        except Exception as e:
            results["errors"] += 1
            results["details"].append({
                "file": rel_path,
                "status": "ERROR",
                "error": str(e)
            })

    # Check for new files not in baseline
    current_files = set()
    for path_name in MONITORED_PATHS:
        path = JARVIS_ROOT / path_name
        if not path.exists():
            continue
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if not should_exclude(Path(root) / d)]
            for f in files:
                fp = Path(root) / f
                if should_exclude(fp):
                    continue
                try:
                    rel_path = fp.relative_to(JARVIS_ROOT)
                    current_files.add(str(rel_path))
                except:
                    pass

    baseline_set = set(baseline_files.keys())
    new_files = current_files - baseline_set
    for new_file in new_files:
        results["new_files"] += 1
        results["details"].append({
            "file": new_file,
            "status": "NEW_FILE"
        })

    return results


def save_baseline(baseline: Dict[str, Any]):
    """Save baseline to file."""
    SECURITY_DIR.mkdir(parents=True, exist_ok=True)
    with open(BASELINE_FILE, "w") as f:
        json.dump(baseline, f, indent=2)
    print(f"Baseline saved to {BASELINE_FILE}")


def load_baseline() -> Dict[str, Any]:
    """Load baseline from file."""
    if BASELINE_FILE.exists():
        with open(BASELINE_FILE) as f:
            return json.load(f)
    return {}


def save_results(results: Dict[str, Any]):
    """Save verification results."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = RESULTS_DIR / f"integrity_{timestamp}.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {results_file}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="J.A.R.V.I.S. Integrity Check")
    parser.add_argument("--create", action="store_true", help="Create new baseline")
    parser.add_argument("--verify", action="store_true", help="Verify against baseline")
    parser.add_argument("--report", action="store_true", help="Show detailed report")

    args = parser.parse_args()

    if args.create:
        baseline = create_baseline()
        save_baseline(baseline)
        return 0

    baseline = load_baseline()
    if not baseline:
        print("No baseline found. Run with --create first.")
        return 1

    if args.verify:
        results = verify_integrity(baseline)
        save_results(results)

        # Print summary
        print(f"\nINTEGRITY VERIFICATION RESULT")
        print(f"  Checked: {results['total_checked']}")
        print(f"  Passed: {results['passed']}")
        print(f"  Failed: {results['failed']}")
        print(f"  Missing: {results['missing']}")
        print(f"  New Files: {results['new_files']}")
        print(f"  Errors: {results['errors']}")

        if args.report:
            print("\nDETAILS:")
            for detail in results["details"]:
                if detail["status"] != "OK":
                    print(f"  {detail['status']}: {detail['file']}")

        if results["failed"] > 0 or results["missing"] > 0 or results["errors"] > 0:
            print("\n⚠ INTEGRITY ISSUES DETECTED")
            return 1
        else:
            print("\n✓ ALL FILES VERIFIED")
            return 0

    # Default: verify
    return main()


if __name__ == "__main__":
    sys.exit(main())