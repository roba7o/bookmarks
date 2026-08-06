#!/bin/bash
# usage: run locust test files with a name and will save results
# ./locust_load/run_locust.sh <testfile> <name>
uv run locust -f "locust_load/$1" \
    --headless -u 100 -r 10 -t 60s \
    --csv="locust_load/results/$1$2" \
    --html="locust_load/results/$1/$2.html"


