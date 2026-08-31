# Session 13 — Predicate Pushdown Commands

## Create Pushdown Dataset

docker compose run --rm --build processing python create_pushdown_dataset.py

## Inspect Row Groups

docker compose run --rm --build processing python inspect_row_groups.py

## Benchmark Predicate Pushdown

docker compose run --rm --build processing python benchmark_pushdown.py

## Create Amount-Sorted Dataset

docker compose run --rm --build processing python create_sorted_pushdown_dataset.py