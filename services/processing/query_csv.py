import pandas as pd
import time

path = "/data/orders-large.csv"

start = time.perf_counter()

df = pd.read_csv(path)

result = df.loc[
    df["order_id"] > 80000,
    ["order_id", "amount"]
]

elapsed = time.perf_counter() - start

print(f"Rows returned: {len(result)}")
print(f"Columns returned: {list(result.columns)}")
print(f"Duration: {elapsed:.6f}s")