"""
Log a process's CPU usage to CSV until it exits (or Ctrl-C).

usage: uv run python scripts/cpu_log.py <pid> <out.csv>

timestamp is unix seconds (lines up with Locust's stats history).
cpu_percent is summed over the pid and its children, 100 = one full core.
"""

import csv
import sys
import time

import psutil

INTERVAL_S = 0.5


def sample(root, seen):
    """Total cpu% for root + children since the last call."""
    cpu = 0.0
    for proc in [root, *root.children(recursive=True)]:
        # reuse the same Process object: cpu_percent measures since its last call
        proc = seen.setdefault(proc.pid, proc)
        try:
            cpu += proc.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            seen.pop(proc.pid, None)
    return cpu


def main():
    root = psutil.Process(int(sys.argv[1]))
    seen = {}
    with open(sys.argv[2], "w", newline="") as out:
        writer = csv.writer(out)
        writer.writerow(["timestamp", "cpu_percent"])
        try:
            sample(root, seen)  # first reading is always 0, throw it away
            while root.is_running():
                time.sleep(INTERVAL_S)
                writer.writerow([f"{time.time():.2f}", f"{sample(root, seen):.1f}"])
                out.flush()
        except (psutil.NoSuchProcess, KeyboardInterrupt):
            pass


if __name__ == "__main__":
    main()
