import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import os
import time

csv_path = "/data/orders-large.csv"
parquet_path = "/output/orders-large.parquet"

start = time.perf_counter()

df = pd.read_csv(csv_path)

# df.to_parquet(
#     parquet_path,
#     engine="pyarrow",
#     compression="snappy"
# )

table = pa.Table.from_pandas(df)

pq.write_table(
    table,
    parquet_path,
    compression="snappy",
    row_group_size=25_000
)

elapsed = time.perf_counter() - start

csv_size = os.path.getsize(csv_path)
parquet_size = os.path.getsize(parquet_path)

print(f"Rows: {len(df):,}")
print(f"CSV size: {csv_size / 1024 / 1024:.2f} MB")
print(f"Parquet size: {parquet_size / 1024 / 1024:.2f} MB")
print(f"Conversion time: {elapsed:.2f}s")