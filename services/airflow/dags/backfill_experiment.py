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

        print("=== BACKFILL EXPERIMENT ===")
        print(f"Logical date: {context['logical_date']}")
        print(f"Data interval start: {context['data_interval_start']}")
        print(f"Data interval end: {context['data_interval_end']}")

    show_data_interval()


backfill_experiment()