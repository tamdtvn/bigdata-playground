import os
import shutil
import time

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


INPUT = "/data/orders-partition.csv"
OUTPUT = "/output/partitioning"


def reset_directory(path):
    if os.path.exists(path):
        shutil.rmtree(path)

    os.makedirs(path)


def write_parquet(df, path):
    table = pa.Table.from_pandas(
        df,
        preserve_index=False
    )

    pq.write_table(
        table,
        path,
        compression="snappy"
    )


print("Reading source CSV...")

df = pd.read_csv(
    INPUT,
    parse_dates=["order_date"]
)

df["month"] = df["order_date"].dt.month
df["order_date"] = df["order_date"].dt.date

print(f"Rows: {len(df):,}")


# --------------------------------------------------
# 1. NON-PARTITIONED
# --------------------------------------------------

path = f"{OUTPUT}/non_partitioned"

reset_directory(path)

start = time.perf_counter()

write_parquet(
    df,
    f"{path}/orders.parquet"
)

elapsed = time.perf_counter() - start

print()
print("=== NON-PARTITIONED ===")
print("Partitions: 1")
print(f"Duration: {elapsed:.3f}s")


# --------------------------------------------------
# 2. PARTITION BY MONTH
# --------------------------------------------------

path = f"{OUTPUT}/by_month"

reset_directory(path)

start = time.perf_counter()

months = df.groupby("month")

for month, group in months:
    partition_path = f"{path}/month={month}"

    os.makedirs(partition_path)

    write_parquet(
        group,
        f"{partition_path}/orders.parquet"
    )

elapsed = time.perf_counter() - start

print()
print("=== BY MONTH ===")
print(f"Partitions: {df['month'].nunique()}")
print(f"Duration: {elapsed:.3f}s")


# --------------------------------------------------
# 3. PARTITION BY DAY
# --------------------------------------------------

path = f"{OUTPUT}/by_day"

reset_directory(path)

start = time.perf_counter()

days = df.groupby("order_date")

for order_date, group in days:
    partition_path = (
        f"{path}/partition_date={order_date}"
    )

    os.makedirs(partition_path)

    write_parquet(
        group,
        f"{partition_path}/orders.parquet"
    )

elapsed = time.perf_counter() - start

print()
print("=== BY DAY ===")
print(f"Partitions: {df['order_date'].nunique()}")
print(f"Duration: {elapsed:.3f}s")