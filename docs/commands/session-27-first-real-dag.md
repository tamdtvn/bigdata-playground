
## Get Login password

    > docker compose exec airflow cat /opt/airflow/simple_auth_manager_passwords.json.generated

    volumes:
        - airflow_data:/opt/airflow

    First startup
        ↓
    Airflow generates password
        ↓
    /opt/airflow/simple_auth_manager_passwords.json.generated
        ↓
    stored in airflow_data volume
        ↓
    container restart/recreate
        ↓
    file still exists
        ↓
    Airflow DOES NOT generate another password

## Check Status

### Pre-flight Validation

    docker compose build airflow

    docker compose up -d airflow

    docker compose ps

    docker compose logs -f airflow

    docker compose exec airflow ls -la /processing

    docker compose exec airflow ls -la /lake/raw/orders

    docker compose exec airflow python -c "import pandas; import pyarrow; print('OK')"

### Check evidence
    docker compose exec airflow ls -lh /lake/cleaned/orders
    docker compose exec airflow ls -lh /lake/curated/daily_revenue
    docker compose exec airflow ls -lh /lake/curated/monthly_revenue

## Expectation

    ┌─────────────────────────────────┐
    │ Airflow                         │
    │                                 │
    │ orchestration                   │
    │ dependency / state / history    │
    └──────────────┬──────────────────┘
                │ invokes
                ▼
    ┌─────────────────────────────────┐
    │ Processing                      │
    │                                 │
    │ validation / transform /        │
    │ aggregation                     │
    └──────────────┬──────────────────┘
                │
                ▼
    ┌─────────────────────────────────┐
    │ Data Lake                       │
    │                                 │
    │ raw → cleaned → curated         │
    └─────────────────────────────────┘

    AIRFLOW
    │
    ▼
    Raw CSV
    │
    ▼
    build_cleaned_orders.py
    │
    ▼
    Cleaned Parquet
    │
    ▼
    build_revenue_curated.py
    │
    ├─────────────┐
    ▼             ▼
    daily_revenue  monthly_revenue


    CONTROL PLANE EVIDENCE
    Airflow
    │
    ├─ cleaned SUCCESS
    └─ curated SUCCESS
            │
            ▼
    DATA PLANE EVIDENCE
    Data Lake
    │
    ├─ cleaned/orders.parquet
    ├─ daily_revenue/daily_revenue.parquet
    └─ monthly_revenue/monthly_revenue.parquet

## Check Evidence data

    docker compose exec airflow ls -lh /lake/cleaned/orders

    docker compose exec airflow ls -lh /lake/curated/daily_revenue

    docker compose exec airflow ls -lh /lake/curated/monthly_revenue