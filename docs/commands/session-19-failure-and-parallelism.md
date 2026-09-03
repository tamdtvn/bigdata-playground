# Session 19 — Failure & Parallelism

## Run Failure Experiment

docker compose run --rm spark /opt/spark/bin/spark-submit /app/failure_experiment.py

## Learning Configuration

Spark local mode:

    local[4,2]

    4: execution threads
    2: allows task failures to be retried in this learning experiment

## Evidence

Successful first attempt:

    (partition_id, 0, row_count)

Retried task:

    (partition_id, 1, row_count)

This experiment demonstrates task-level retry in local mode.

It does not demonstrate recovery from an actual executor machine failure.