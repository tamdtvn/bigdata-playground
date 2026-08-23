import csv

ROWS = 100_000

with open("datasets/orders-large.csv", "w", newline="") as f:
    writer = csv.writer(f)

    writer.writerow([
        "order_id",
        "customer_id",
        "product",
        "amount",
    ])

    for i in range(1, ROWS + 1):
        writer.writerow([
            i,
            1000 + (i % 1000),
            f"Product-{i % 100}",
            10 + (i % 500),
        ])

print(f"Generated {ROWS} orders.")