import os
import pandas as pd
import pyarrow.parquet as pq

INPUT = "/lake/cleaned/orders/orders.parquet"

DAILY_DIR = "/lake/curated/daily_revenue"
MONTHLY_DIR = "/lake/curated/monthly_revenue"

DAILY_OUTPUT = f"{DAILY_DIR}/daily_revenue.parquet"
MONTHLY_OUTPUT = f"{MONTHLY_DIR}/monthly_revenue.parquet"

os.makedirs(DAILY_DIR, exist_ok=True)
os.makedirs(MONTHLY_DIR, exist_ok=True)

print("Reading cleaned orders...")
df = pd.read_parquet(INPUT)

df["order_date"] = pd.to_datetime(df["order_date"])

daily = (
    df.groupby("order_date", as_index=False)
      .agg(
          total_orders=("order_id", "count"),
          total_revenue=("amount", "sum"),
      )
)

daily.to_parquet(
    DAILY_OUTPUT,
    index=False
)

df["order_month"] = (
    df["order_date"]
      .dt.to_period("M")
      .astype(str)
)

monthly = (
    df.groupby("order_month", as_index=False)
      .agg(
          total_orders=("order_id", "count"),
          total_revenue=("amount", "sum"),
      )
)

monthly.to_parquet(
    MONTHLY_OUTPUT,
    index=False
)

print(f"Daily rows: {len(daily)}")
print(f"Created: {DAILY_OUTPUT}")

print(f"Monthly rows: {len(monthly)}")
print(f"Created: {MONTHLY_OUTPUT}")