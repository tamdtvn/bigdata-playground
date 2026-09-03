# Session 17 — Spark Fundamentals

## Run Spark Job

docker compose run --rm spark /opt/spark/bin/spark-submit /app/first_spark_job.py

## Important Debugging Tool

DataFrame.explain("formatted")

Use it to inspect how Spark plans to execute a query.

## IMPORTANT Mental Model

    Application Intent  [Requirement]
            ↓
    Lazy Evaluation [Waiting for Clarification]
            ↓
    Optimizer [Adjustment]
            │
            ├── Column Pruning ✓
            └── Predicate Pushdown ✓
            ↓
    Physical Plan [Implementation Plan]
            ↓
    Processing Partitions
            ↓
    Tasks / Execution


Lazy Evaluation

    read
    ↓
    filter
    ↓
    select
    ↓
            "Đợi đã, chưa chạy."
    ↓
    action
    ↓
    "Bây giờ đã biết đủ yêu cầu,
    hãy optimize toàn bộ rồi chạy."


MOST IMPORTANT: This session already connected SPRINT 3 + SPRINT 4

    SPRINT 3
    How should data be stored?
            │
            ├── Parquet
            ├── Row Groups
            ├── Column Pruning
            ├── Predicate Pushdown
            └── Data Skipping
            │
            ▼
    SPRINT 4
    How should computation be distributed?
            │
            ├── Spark Partition
            ├── Task
            ├── Driver / Executor
            └── Parallelism    