# from airflow.sdk import dag, task
# from datetime import datetime
# import time


# @dag(
#     dag_id="big_data_playground",
#     schedule=None,
#     start_date=datetime(2026, 1, 1),
#     catchup=False,
# )

# def big_data_playground():

#     @task
#     def build_cleaned_orders():
#         print("Building cleaned orders...")
#         time.sleep(10)
#         print("Cleaned orders completed.")

#     @task
#     def build_revenue_curated():
#         print("Building revenue curated data...")
#         time.sleep(10)
#         print("Revenue curated completed.")

#     cleaned = build_cleaned_orders()
#     curated = build_revenue_curated()

#     # cleaned >> curated


# big_data_playground()

from airflow.sdk import dag, task
from datetime import datetime
import subprocess


@dag(
    dag_id="big_data_playground",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
)
def big_data_playground():

    @task
    def build_cleaned_orders():
        subprocess.run(
            ["python", "/processing/build_cleaned_orders.py"],
            check=True,
        )

    @task
    def build_revenue_curated():
        subprocess.run(
            ["python", "/processing/build_revenue_curated.py"],
            check=True,
        )

    cleaned = build_cleaned_orders()
    curated = build_revenue_curated()

    cleaned >> curated


big_data_playground()