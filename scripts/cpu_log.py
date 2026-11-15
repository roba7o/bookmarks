"""
Log a process's CPU usage to CSV until it exits (or Ctrl-C).

usage: uv run python scripts/cpu_log.py <pid> [out.csv] [--interval 0.5]

cpu_percent is summed over the pid and its children, 100 = one full core.
"""

import argparse
import csv
import sys
import time

import psutil


def sample(root, seen):
    """Total cpu% and thread count for root + children since the last call."""
    cpu, threads = 0.0, 0
    for proc in [root, *root.children(recursive=True)]:
        # reuse the same Process object: cpu_percent measures since its last call
        proc = seen.setdefault(proc.pid, proc)
        try:
            cpu += proc.cpu_percent(interval=None)
            threads += proc.num_threads()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            seen.pop(proc.pid, None)
    return cpu, threads


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pid", type=int)
    parser.add_argument("out", nargs="?", help="csv path, default stdout")
    parser.add_argument("--interval", type=float, default=0.5)
    args = parser.parse_args()

    root = psutil.Process(args.pid)
    out = open(args.out, "w", newline="") if args.out else sys.stdout
    writer = csv.writer(out)
    writer.writerow(["elapsed_s", "cpu_percent", "threads"])

    seen = {}
    start = time.monotonic()
    try:
        sample(root, seen)  # first reading is always 0, throw it away
        while root.is_running():
            time.sleep(args.interval)
            cpu, threads = sample(root, seen)
            writer.writerow([f"{time.monotonic() - start:.2f}", f"{cpu:.1f}", threads])
            out.flush()
    except (psutil.NoSuchProcess, KeyboardInterrupt):
        pass
    finally:
        out.close()


if __name__ == "__main__":
    main()
