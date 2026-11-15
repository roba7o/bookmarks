#!/bin/bash
# bcrypt threadpool experiment: for each user count and mode, start the server,
# load it with Locust, and log its CPU. Plot with scripts/plot_experiment.py.
#
# usage: ./locust_load/run_experiment.sh
# knobs (env vars): USERS_LIST="10 25 50 100 200" REPEATS=3 DURATION=45s LOGIN_WEIGHT=1
set -euo pipefail
cd "$(dirname "$0")/.."

REPEATS="${REPEATS:-3}"
USERS_LIST="${USERS_LIST:-10 25 50 100 200}"
DURATION="${DURATION:-45s}"
export LOGIN_WEIGHT="${LOGIN_WEIGHT:-1}"

URL="http://localhost:8000"
outroot="locust_load/results/experiment/$(date +'%d%m%Y-%H%M')"
server_pid=""

# poll a command once a second until it succeeds: wait_for <seconds> <cmd...>
wait_for() {
    local tries=$1
    shift
    until "$@" >/dev/null 2>&1; do
        tries=$((tries - 1))
        [ "$tries" -gt 0 ] || return 1
        sleep 1
    done
}

server_up() { curl -s -o /dev/null "$URL/bookmarks"; }

stop_server() {
    [ -n "$server_pid" ] || return 0
    pkill -TERM -P "$server_pid" 2>/dev/null || true # uvicorn, child of `uv run`
    kill "$server_pid" 2>/dev/null || true
    wait "$server_pid" 2>/dev/null || true
    server_pid=""
}
trap stop_server EXIT # also runs on Ctrl-C / errors

# --- 1. database -----------------------------------------------------------
if ! docker info >/dev/null 2>&1; then
    echo "starting Docker..."
    open -a Docker
    wait_for 120 docker info || { echo "Docker did not start"; exit 1; }
fi
docker compose up -d db
wait_for 60 docker compose exec -T db pg_isready || { echo "Postgres not ready"; exit 1; }

if server_up; then
    echo "something is already listening on $URL, stop it first"
    exit 1
fi

# --- 2. one run per (repeat, user count, mode) ------------------------------
for run in $(seq 1 "$REPEATS"); do
  for users in $USERS_LIST; do
    for mode in true false; do
        outdir="$outroot/users_${users}_threadpool_${mode}_run${run}"
        mkdir -p "$outdir"
        echo "=== users=$users threadpool=$mode run=$run -> $outdir"

        BCRYPT_IN_THREADPOOL="$mode" uv run uvicorn src.bookmarks.main:app \
            >"$outdir/server.log" 2>&1 &
        server_pid=$!
        wait_for 30 server_up || { echo "server did not start:"; cat "$outdir/server.log"; exit 1; }

        uv run python scripts/ensure_test_user.py

        uv run python scripts/cpu_log.py "$server_pid" "$outdir/cpu.csv" &
        logger_pid=$!

        cat >"$outdir/config.txt" <<EOF
BCRYPT_IN_THREADPOOL=$mode
USERS=$users
RUN=$run
CORES=$(sysctl -n hw.ncpu)
DURATION=$DURATION
LOGIN_WEIGHT=$LOGIN_WEIGHT
EOF

        # locust exits non-zero if any request failed; keep going, it's in the csv
        uv run locust -f locust_load/basic_locust.py --headless \
            -u "$users" -r "$users" -t "$DURATION" \
            --csv="$outdir/locust" --html="$outdir/locust.html" || true

        stop_server
        wait "$logger_pid" 2>/dev/null || true # exits once the server is gone
    done
  done
done

echo "done: $outroot"
