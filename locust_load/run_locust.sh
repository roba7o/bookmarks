#!/bin/bash
# usage: run locust test files with a name and will save results
# ./locust_load/run_locust.sh <testfile> (without.py)
name="${1}_locust.py"
ECHO "Running: $name"


uv run locust -f "locust_load/$name" \
    --headless -u 100 -r 10 -t 60s \
    --csv="locust_load/results/$1/$1" \
    --html="locust_load/results/$1/$1.html"


