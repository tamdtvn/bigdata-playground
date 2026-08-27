import pyarrow.parquet as pq

path = "/output/orders-large.parquet"

parquet_file = pq.ParquetFile(path)
metadata = parquet_file.metadata

print("=== SCHEMA ===")
print(parquet_file.schema)

print()
print("=== METADATA ===")
print(f"Rows: {metadata.num_rows}")
print(f"Columns: {metadata.num_columns}")
print(f"Row groups: {metadata.num_row_groups}")

print()
print("=== ROW GROUP STATISTICS ===")

for i in range(metadata.num_row_groups):
    row_group = metadata.row_group(i)

    print(f"\nRow Group {i + 1}")
    print(f"Rows: {row_group.num_rows}")

    order_id_column = row_group.column(0)
    stats = order_id_column.statistics

    print(f"order_id min: {stats.min}")
    print(f"order_id max: {stats.max}")