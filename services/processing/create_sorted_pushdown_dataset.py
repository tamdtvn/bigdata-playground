import os

import pyarrow.compute as pc
import pyarrow.parquet as pq


INPUT = "/output/pushdown/orders.parquet"
OUTPUT_DIR = "/output/pushdown_sorted"
OUTPUT = f"{OUTPUT_DIR}/orders.parquet"

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Reading existing Parquet...")

table = pq.read_table(INPUT)

print(f"Rows: {table.num_rows}")

# Sort by amount ascending
sort_indices = pc.sort_indices(
    table,
    sort_keys=[("amount", "ascending")]
)

sorted_table = pc.take(table, sort_indices)

pq.write_table(
    sorted_table,
    OUTPUT,
    row_group_size=100_000
)

parquet_file = pq.ParquetFile(OUTPUT)

print(f"Created: {OUTPUT}")
print(f"Row groups: {parquet_file.num_row_groups}")