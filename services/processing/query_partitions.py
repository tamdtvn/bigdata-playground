import time
from datetime import date

import pyarrow.dataset as ds


TARGET_DATE = date(2026, 8, 28)
TARGET_MONTH = 8
TARGET_PARTITION_DATE = "2026-08-28"


def run_query(name, path, partition_filter=None):
    dataset = ds.dataset(
        path,
        format="parquet",
        partitioning="hive"
    )

    business_filter = (
        ds.field("order_date") == TARGET_DATE
    )

    if partition_filter is not None:
        query_filter = partition_filter & business_filter
    else:
        query_filter = business_filter

    start = time.perf_counter()

    table = dataset.to_table(
        columns=["order_date", "amount"],
        filter=query_filter
    )

    elapsed = time.perf_counter() - start

    revenue = sum(
        table["amount"].to_pylist()
    )

    print()
    print(f"=== {name} ===")
    print(f"Rows returned: {table.num_rows}")
    print(f"Revenue: {revenue}")
    print(f"Duration: {elapsed:.6f}s")


run_query(
    "NON-PARTITIONED",
    "/output/partitioning/non_partitioned"
)

run_query(
    "BY MONTH",
    "/output/partitioning/by_month",
    ds.field("month") == TARGET_MONTH
)

run_query(
    "BY DAY",
    "/output/partitioning/by_day",
    ds.field("partition_date") == TARGET_PARTITION_DATE
)