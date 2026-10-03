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