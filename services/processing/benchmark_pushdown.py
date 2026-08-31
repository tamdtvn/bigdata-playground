import time

import pyarrow.compute as pc
import pyarrow.dataset as ds


# PATH = "/output/pushdown/orders.parquet"
PATH = "/output/pushdown_sorted/orders.parquet"


def benchmark_after_read(name, predicate):
    dataset = ds.dataset(PATH, format="parquet")

    start = time.perf_counter()

    # Read first
    table = dataset.to_table()

    # Filter after data has been materialized
    result = predicate(table)

    elapsed = time.perf_counter() - start

    print(
        f"{name:<30} "
        f"Rows={result.num_rows:<10} "
        f"Duration={elapsed:.6f}s"
    )


def benchmark_pushdown(name, predicate):
    dataset = ds.dataset(PATH, format="parquet")

    start = time.perf_counter()

    # Give predicate directly to the dataset reader
    result = dataset.to_table(
        filter=predicate
    )

    elapsed = time.perf_counter() - start

    print(
        f"{name:<30} "
        f"Rows={result.num_rows:<10} "
        f"Duration={elapsed:.6f}s"
    )


print()
print("=== ORDER_ID > 900000 ===")

benchmark_after_read(
    "AFTER READ",
    lambda table: table.filter(
        pc.greater(
            table["order_id"],
            900000
        )
    )
)

benchmark_pushdown(
    "PUSHDOWN",
    ds.field("order_id") > 900000
)


print()
print("=== AMOUNT > 900 ===")

benchmark_after_read(
    "AFTER READ",
    lambda table: table.filter(
        pc.greater(
            table["amount"],
            900
        )
    )
)

benchmark_pushdown(
    "PUSHDOWN",
    ds.field("amount") > 900
)