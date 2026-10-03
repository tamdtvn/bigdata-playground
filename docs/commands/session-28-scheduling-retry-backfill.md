
# Session 28 — Scheduling, Retry & Backfill

## 1. Scheduling

Update the main DAG:

```python
@dag(
    dag_id="big_data_playground",
    schedule="*/5 * * * *",
    start_date=datetime(2026, 9, 12),
    catchup=False,
)
```

Save the DAG and wait for an automatically scheduled run.

## 2. Retry

Add an experimental task:

```python
from datetime import timedelta
from airflow.sdk import task, get_current_context

@task(
    retries=2,
    retry_delay=timedelta(seconds=10),
)
def transient_failure_test():
    context = get_current_context()
    task_instance = context["ti"]

    if task_instance.try_number == 1:
        raise RuntimeError("Intentional transient failure")

    print("Recovered successfully.")
```

Temporary dependency:

```python
retry_test >> cleaned >> curated
```

Observed result:

- First attempt failed intentionally.
- Second attempt succeeded.
- Downstream tasks completed successfully.

## 3. Backfill

Experimental DAG:

```python
from airflow.sdk import dag, task, get_current_context
from datetime import datetime

@dag(
    dag_id="backfill_experiment",
    schedule="@daily",
    start_date=datetime(2026, 9, 7),
    catchup=False,
)
def backfill_experiment():

    @task
    def show_data_interval():
        context = get_current_context()

        print(f"Logical date: {context['logical_date']}")
        print(f"Data interval start: {context['data_interval_start']}")
        print(f"Data interval end: {context['data_interval_end']}")

    show_data_interval()

backfill_experiment()
```

Dry run:

```bash
docker compose exec airflow airflow backfill create \
  --dag-id backfill_experiment \
  --from-date 2026-09-08T00:00:00+00:00 \
  --to-date 2026-09-10T00:00:00+00:00 \
  --dry-run
```

Create backfill:

```bash
docker compose exec airflow airflow backfill create \
  --dag-id backfill_experiment \
  --from-date 2026-09-08T00:00:00+00:00 \
  --to-date 2026-09-10T00:00:00+00:00 \
  --reprocess-behavior none
```

Observed result:

Three historical DAG Runs were created for September 8, 9, and 10, 2026.

In the observed task logs, each run's data interval start and end were equal to its logical date.

## 4. Cleanup Before the Next Session

Restore the main DAG's schedule to `None` if automatic runs are no longer needed.

Remove the temporary retry task and restore:

```python
cleaned >> curated
```

Keep `backfill_experiment.py` as a reproducible learning experiment. Pause its DAG in Airflow to avoid unnecessary scheduled executions.
