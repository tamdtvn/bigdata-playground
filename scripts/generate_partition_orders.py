import csv
import random
from datetime import date, timedelta

ROWS = 1_000_000

start_date = date(2026, 1, 1)
number_of_days = 365

products = [
    "Coffee",
    "Tea",
    "Sandwich",
    "Cake",
    "Juice"
]

output_path = "/output/orders-partition.csv"

random.seed(42) # random generation become deterministic: same generated dataset each RUN

with open(output_path, "w", newline="") as file:
    writer = csv.writer(file)

    writer.writerow([
        "order_id",
        "customer_id",
        "product",
        "amount",
        "order_date"
    ])

    for order_id in range(1, ROWS + 1):
        order_date = start_date + timedelta(
            days=random.randrange(number_of_days)
        )

        writer.writerow([
            order_id,
            random.randint(1, 100_000),
            random.choice(products),
            random.randint(10, 1000),
            order_date.isoformat()
        ])

print(f"Generated {ROWS:,} orders")
print(f"Output: {output_path}")