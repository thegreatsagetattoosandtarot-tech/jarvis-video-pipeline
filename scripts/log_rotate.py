#!/usr/bin/env python3
"""
J.A.R.V.I.S. OS - Log Rotation Script
Rotates and compresses old logs.
"""

import asyncio
import gzip
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path

JARVIS_ROOT = Path("/opt/data/JARVIS_OS")
LOGS_DIR = JARVIS_ROOT / "logs"


async def rotate_logs(max_age_days: int = 30, max_size_mb: int = 100, compress: bool = True):
    """Rotate logs based on age and size."""
    cutoff_date = datetime.now() - timedelta(days=max_age_days)
    rotated = 0
    compressed = 0
    removed = 0

    for log_file in LOGS_DIR.rglob("*.log"):
        # Check age
        mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
        if mtime < cutoff_date:
            if compress and log_file.suffix != ".gz":
                # Compress
                gz_path = log_file.with_suffix(log_file.suffix + ".gz")
                with open(log_file, "rb") as f_in:
                    with gzip.open(gz_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
                log_file.unlink()
                print(f"Compressed: {log_file.name} -> {gz_path.name}")
                compressed += 1
            else:
                # Remove old compressed logs
                if log_file.suffix == ".gz":
                    log_file.unlink()
                    print(f"Removed old compressed log: {log_file.name}")
                    removed += 1
        else:
            # Check size for active logs
            size_mb = log_file.stat().st_size / (1024 * 1024)
            if size_mb > max_size_mb:
                # Rotate: rename current, create new
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                rotated_name = log_file.with_name(f"{log_file.stem}_{timestamp}.log")
                log_file.rename(rotated_name)
                log_file.touch()
                print(f"Rotated large log: {log_file.name} -> {rotated_name.name} ({size_mb:.1f} MB)")
                rotated += 1

                if compress:
                    gz_path = rotated_name.with_suffix(rotated_name.suffix + ".gz")
                    with open(rotated_name, "rb") as f_in:
                        with gzip.open(gz_path, "wb") as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    rotated_name.unlink()
                    compressed += 1

    print(f"\nLog rotation complete: {rotated} rotated, {compressed} compressed, {removed} removed")
    return {"rotated": rotated, "compressed": compressed, "removed": removed}


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="J.A.R.V.I.S. OS Log Rotation")
    parser.add_argument("--max-age", type=int, default=30, help="Max age in days")
    parser.add_argument("--max-size", type=int, default=100, help="Max size in MB")
    parser.add_argument("--no-compress", action="store_true", help="Don't compress")
    args = parser.parse_args()

    print("=" * 60)
    print(f"J.A.R.V.I.S. OS Log Rotation - {datetime.now().isoformat()}")
    print("=" * 60)

    await rotate_logs(
        max_age_days=args.max_age,
        max_size_mb=args.max_size,
        compress=not args.no_compress
    )

    print("\nLog rotation complete.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))