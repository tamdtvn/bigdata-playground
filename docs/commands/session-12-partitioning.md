# Session 12 — Partitioning Commands

## Generate Dataset

    docker compose run --rm data-generator

## Create Partition Layouts

    docker compose run --rm --build processing python create_partitions.py

## Daily Revenue Benchmark

    docker compose run --rm --build processing python query_partitions.py

## Monthly and Yearly Workloads

    docker compose run --rm --build processing python query_partition_workloads.py

## Validate Compose

    docker compose config