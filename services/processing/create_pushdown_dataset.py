import os
import pyarrow.csv as csv
import pyarrow.parquet as pq


INPUT = "/data/orders-partition.csv"
OUTPUT_DIR = "/output/pushdown"
OUTPUT = f"{OUTPUT_DIR}/orders.parquet"

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Reading source data...")

table = csv.read_csv(INPUT)

print(f"Rows: {table.num_rows}")

pq.write_table(
    table,
    OUTPUT,
    row_group_size=100_000
)

parquet_file = pq.ParquetFile(OUTPUT)

print(f"Created: {OUTPUT}")
print(f"Row groups: {parquet_file.num_row_groups}")