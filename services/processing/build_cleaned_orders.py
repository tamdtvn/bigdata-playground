import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

INPUT = "/lake/raw/orders/orders-partition.csv"
OUTPUT_DIR = "/lake/cleaned/orders"
OUTPUT = f"{OUTPUT_DIR}/orders.parquet"

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Reading raw orders...")
df = pd.read_csv(INPUT)

print(f"Raw rows: {len(df)}")
print(f"Columns: {list(df.columns)}")

required_columns = {
    "order_id",
    "customer_id",
    "product",
    "amount",
    "order_date",
}

missing_columns = required_columns - set(df.columns)

if missing_columns:
    raise ValueError(
        f"Missing required columns: {sorted(missing_columns)}"
    )

if df[list(required_columns)].isnull().any().any():
    raise ValueError("Null values found in required columns")

df["order_id"] = pd.to_numeric(
    df["order_id"],
    errors="raise"
).astype("int64")

df["customer_id"] = pd.to_numeric(
    df["customer_id"],
    errors="raise"
).astype("int64")

df["amount"] = pd.to_numeric(
    df["amount"],
    errors="raise"
).astype("int64")

df["order_date"] = pd.to_datetime(
    df["order_date"],
    errors="raise"
).dt.date

if df["order_id"].duplicated().any():
    raise ValueError("Duplicate order_id found")

if (df["amount"] < 0).any():
    raise ValueError("Negative amount found")

table = pa.Table.from_pandas(
    df,
    preserve_index=False
)

pq.write_table(
    table,
    OUTPUT,
    row_group_size=100_000
)

print(f"Cleaned rows: {len(df)}")
print(f"Created: {OUTPUT}")