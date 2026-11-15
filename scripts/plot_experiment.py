"""
Plot a run_experiment.sh results folder: server CPU and /bookmarks p95
against user count, threadpool on vs off.

usage: uv run python scripts/plot_experiment.py [results_dir]
       results_dir defaults to the newest folder in locust_load/results/experiment
writes: ignore/blog/bcrypt_threadpool.png
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RESULTS = Path("locust_load/results/experiment")
OUT = Path("ignore/blog/bcrypt_threadpool.png")
WARMUP_S = 5  # skip the ramp-up at the start of each run

SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#898781", "#e8e7e3"
MODES = {  # BCRYPT_IN_THREADPOOL value -> (label, colour)
    "true": ("threadpool on", "#2a78d6"),
    "false": ("threadpool off (event loop)", "#eb6834"),
}
PANELS = [  # (key in a run, title, log scale?)
    ("cpu", "Server CPU (%, 100 = one core)", False),
    ("bookmarks_p95", "/bookmarks p95 response time (ms, log scale)", True),
]

plt.rcParams.update(
    {
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "axes.edgecolor": MUTED,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": GRID,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelcolor": INK,
        "ytick.labelcolor": INK,
        "lines.linewidth": 2,
        "legend.frameon": False,
    }
)


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def load_run(rundir):
    config = dict(
        line.split("=", 1) for line in (rundir / "config.txt").read_text().split()
    )
    stats = {row["Name"]: row for row in read_csv(rundir / "locust_stats.csv")}

    # Locust's clock defines the run window; cpu.csv starts a little earlier
    times = [
        float(r["Timestamp"]) for r in read_csv(rundir / "locust_stats_history.csv")
    ]
    cpu = [
        float(r["cpu_percent"])
        for r in read_csv(rundir / "cpu.csv")
        if min(times) + WARMUP_S <= float(r["timestamp"]) <= max(times)
    ]
    return {
        "mode": config["BCRYPT_IN_THREADPOOL"],
        "users": int(config["USERS"]),
        "cores": int(config["CORES"]),
        "cpu": mean(cpu),
        "bookmarks_p95": float(stats["/bookmarks"]["95%"]),
    }


def plot(runs):
    """One point per user count (mean of repeats), one line per mode."""
    user_levels = sorted({r["users"] for r in runs})
    fig, axes = plt.subplots(len(PANELS), 1, figsize=(8, 7), sharex=True)

    for ax, (key, title, log) in zip(axes, PANELS):
        for mode, (label, colour) in MODES.items():
            by_users = defaultdict(list)
            for r in runs:
                if r["mode"] == mode:
                    by_users[r["users"]].append(r[key])
            xs = sorted(by_users)
            # every repeat as a faint dot, the mean as the line
            for x in xs:
                ax.scatter(
                    [x] * len(by_users[x]), by_users[x], s=14, color=colour, alpha=0.3
                )
            ax.plot(
                xs,
                [mean(by_users[x]) for x in xs],
                color=colour,
                label=label,
                marker="o",
                markersize=7,
                markeredgecolor=SURFACE,
                markeredgewidth=1.5,
            )
        ax.set_title(title)
        if log:
            ax.set_yscale("log")
        else:
            ax.set_ylim(bottom=0)

    axes[0].axhline(100, color=MUTED, linewidth=1, linestyle="--")
    axes[0].annotate(
        "one core",
        (user_levels[-1], 100),
        xytext=(0, 4),
        textcoords="offset points",
        ha="right",
        color=MUTED,
        fontsize=9,
    )
    axes[-1].set_xlabel("Concurrent Locust users")
    axes[-1].set_xticks(user_levels)

    fig.suptitle(
        f"bcrypt: event loop vs threadpool ({runs[0]['cores']}-core machine)",
        x=0.06,
        ha="left",
        fontsize=13,
        fontweight="bold",
    )
    fig.legend(
        *axes[0].get_legend_handles_labels(),
        loc="upper left",
        bbox_to_anchor=(0.06, 0.955),
        ncols=2,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.925))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=200)


def main():
    if len(sys.argv) > 1:
        results = Path(sys.argv[1])
    else:
        results = max(RESULTS.iterdir(), key=lambda p: p.stat().st_mtime)
    runs = [load_run(d) for d in sorted(results.iterdir()) if d.is_dir()]
    plot(runs)
    print(f"{len(runs)} runs from {results} -> {OUT}")


if __name__ == "__main__":
    main()
