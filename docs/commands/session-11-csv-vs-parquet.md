# Session 11 — CSV vs Parquet Commands

## Convert CSV to Parquet

    docker compose run --rm --build processing python csv_to_parquet.py

## Inspect Parquet

    docker compose run --rm --build processing python inspect_parquet.py

## Query Parquet

    docker compose run --rm --build processing python query_parquet.py

## Query CSV

    docker compose run --rm --build processing python query_csv.py