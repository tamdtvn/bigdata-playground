import time
from datetime import date

import pyarrow.dataset as ds


DATASETS = {
    "NON-PARTITIONED":
        "/output/partitioning/non_partitioned",

    "BY MONTH":
        "/output/partitioning/by_month",

    "BY DAY":
        "/output/partitioning/by_day",
}


def load_dataset(path):
    return ds.dataset(
        path,
        format="parquet",
        partitioning="hive"
    )


def execute(name, dataset, query_filter):
    start = time.perf_counter()

    table = dataset.to_table(
        columns=["amount"],
        filter=query_filter
    )

    elapsed = time.perf_counter() - start

    revenue = sum(table["amount"].to_pylist())

    print(
        f"{name:<18} "
        f"Rows={table.num_rows:<8} "
        f"Revenue={revenue:<12} "
        f"Duration={elapsed:.6f}s"
    )


datasets = {
    name: load_dataset(path)
    for name, path in DATASETS.items()
}


# --------------------------------------------------
# MONTHLY REVENUE — AUGUST 2026
# --------------------------------------------------

print()
print("=== MONTHLY REVENUE: 2026-08 ===")

start_date = date(2026, 8, 1)
end_date = date(2026, 9, 1)

business_filter = (
    (ds.field("order_date") >= start_date)
    &
    (ds.field("order_date") < end_date)
)

execute(
    "NON-PARTITIONED",
    datasets["NON-PARTITIONED"],
    business_filter
)

execute(
    "BY MONTH",
    datasets["BY MONTH"],
    (ds.field("month") == 8)
    &
    business_filter
)

execute(
    "BY DAY",
    datasets["BY DAY"],
    (
        ds.field("partition_date") >= "2026-08-01"
    )
    &
    (
        ds.field("partition_date") < "2026-09-01"
    )
    &
    business_filter
)


# --------------------------------------------------
# YEARLY REVENUE — 2026
# --------------------------------------------------

print()
print("=== YEARLY REVENUE: 2026 ===")

start_date = date(2026, 1, 1)
end_date = date(2027, 1, 1)

business_filter = (
    (ds.field("order_date") >= start_date)
    &
    (ds.field("order_date") < end_date)
)

execute(
    "NON-PARTITIONED",
    datasets["NON-PARTITIONED"],
    business_filter
)

execute(
    "BY MONTH",
    datasets["BY MONTH"],
    business_filter
)

execute(
    "BY DAY",
    datasets["BY DAY"],
    business_filter
)