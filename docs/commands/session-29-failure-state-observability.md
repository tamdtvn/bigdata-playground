# Session 29 — Failure, State & Observability

## Goal

Create a controlled permanent failure and investigate it using Airflow execution evidence.

## Experiment DAG

Create:

```text
services/airflow/dags/observability_experiment.py
```

```python
from airflow.sdk import dag, task, get_current_context
from datetime import datetime, timedelta


@dag(
    dag_id="observability_experiment",
    schedule=None,
    start_date=datetime(2026, 9, 1),
    catchup=False,
)
def observability_experiment():

    @task(
        retries=2,
        retry_delay=timedelta(seconds=5),
    )
    def extract_data():
        context = get_current_context()
        ti = context["ti"]

        print("=== EXTRACT DATA ===")
        print(f"Run ID: {context['run_id']}")
        print(f"Try number: {ti.try_number}")

        raise FileNotFoundError(
            "/lake/raw/ilostat/input.csv does not exist"
        )

    @task
    def transform_data():
        print("Transforming data...")

    @task
    def publish_data():
        print("Publishing data...")

    extract = extract_data()
    transform = transform_data()
    publish = publish_data()

    extract >> transform >> publish


observability_experiment()
```

## Expected Execution

```text
extract_data
    Attempt 1 → FAIL
    Attempt 2 → FAIL
    Attempt 3 → FAIL
         ↓
    FINAL FAILED
         ↓
transform_data → UPSTREAM FAILED
         ↓
publish_data   → UPSTREAM FAILED
```

## Observed Evidence

```text
DAG Run             FAILED
extract_data         FAILED          Try 3
transform_data       UPSTREAM FAILED Try 0
publish_data         UPSTREAM FAILED Try 0
```

Final failed attempt:

```text
Try number: 3

FileNotFoundError:
/lake/raw/ilostat/input.csv does not exist
```

## Troubleshooting Procedure

```text
DAG State
    ↓
Task States
    ↓
Failed Task
    ↓
Attempts
    ↓
Failed Attempt Log
    ↓
Verify Evidence
    ↓
Root Cause
```

Do not begin by reading every pipeline log.

First localize the failure, then investigate the evidence closest to that failure.

## Cleanup

Keep `observability_experiment.py` as a reproducible learning experiment.

Because the DAG uses:

```python
schedule=None
```

it will not create scheduled runs automatically.