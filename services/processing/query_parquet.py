import pyarrow.parquet as pq
import pyarrow.compute as pc
import time

path = "/output/orders-large.parquet"

start = time.perf_counter()

table = pq.read_table(
    path,
    columns=["order_id", "amount"],
    filters=[
        ("order_id", ">", 80000)
    ]
)

elapsed = time.perf_counter() - start

print(f"Rows returned: {table.num_rows}")
print(f"Columns read: {table.column_names}")
print(f"Duration: {elapsed:.6f}s")

print()
print("First 5 rows:")
print(table.slice(0, 5))