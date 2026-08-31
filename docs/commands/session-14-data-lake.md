# Session 14 - Data Lake Foundation

## Create new data folder
    mkdir data
    mkdir data\lake
    mkdir data\lake\raw
    mkdir data\lake\raw\orders
    mkdir data\lake\cleaned
    mkdir data\lake\cleaned\orders
    mkdir data\lake\curated
    mkdir data\lake\curated\daily_revenue
    mkdir data\lake\curated\monthly_revenue
    mkdir data\experiments

    copy datasets\orders-partition.csv data\lake\raw\orders\orders-partition.csv

## compose.yaml
    processing:
    build:
        context: ../services/processing
    volumes:
        - ../datasets:/data:ro
        - ../datasets/processed:/output

        - ../data/lake/raw:/lake/raw:ro
        - ../data/lake/cleaned:/lake/cleaned
        - ../data/lake/curated:/lake/curated

## Docker run

    docker compose run --rm --build processing python build_cleaned_orders.py

    docker compose run --rm --build processing python build_revenue_curated.py

## Pipeline

                    SOURCE
                        │
                        ▼
        raw/orders/orders-partition.csv
                        │
                        │ build_cleaned_orders.py
                        │
                        ▼
            cleaned/orders/orders.parquet
                        │
                        │ build_revenue_curated.py
                        │
                ┌──────┴──────┐
                ▼             ▼
    daily_revenue       monthly_revenue
        365 rows            12 rows