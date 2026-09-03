# Session 18 — Distributed Aggregation & Shuffle

## Run Experiment

docker compose run --rm spark /opt/spark/bin/spark-submit /app/shuffle_experiment.py

## Inspect Physical Plan

DataFrame.explain("formatted")

## Important Plan Evidence

Shuffle:

    Exchange

Partial Aggregation:

    partial_sum(...)

Adaptive Query Execution:

    AdaptiveSparkPlan

Runtime Shuffle Statistics:

    ShuffleQueryStage
    Statistics(...)

AQE Partition Optimization:

    AQEShuffleRead
    Arguments: coalesced