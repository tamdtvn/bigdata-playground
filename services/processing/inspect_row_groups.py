import pyarrow.parquet as pq

# path = "/output/partitioning/non_partitioned/orders.parquet"
path = "/output/pushdown/orders.parquet"
# path = "/output/pushdown_sorted/orders.parquet"

parquet_file = pq.ParquetFile(path)

print(f"Row groups: {parquet_file.num_row_groups}")
print()

for i in range(parquet_file.num_row_groups):
    rg = parquet_file.metadata.row_group(i)

    print(f"Row Group {i}")

    for column_name in ["order_id", "amount"]:
        column_index = parquet_file.schema.names.index(column_name)
        column = rg.column(column_index)

        stats = column.statistics

        print(
            f"  {column_name:<10} "
            f"min={stats.min:<10} "
            f"max={stats.max:<10}"
        )

    print()