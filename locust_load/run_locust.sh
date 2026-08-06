#!/bin/bash
# usage: ./locust_load/run_locust.sh <name>    e.g. "basic"  (no .py, no _locust)
ts="$(date +'%d%m%Y-%H%M')"                 # 06082026-1442
outdir="locust_load/results/$1/$ts"         # results/basic/06082026-1442/
mkdir -p "$outdir"                          # create it (+ parents)

uv run locust -f "locust_load/${1}_locust.py" \
    -u 100 -r 1000 -t 45s \
    --csv="$outdir/$1" \
    --html="$outdir/$1.html"
