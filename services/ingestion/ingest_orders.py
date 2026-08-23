import csv
import time
import psycopg
from psycopg import OperationalError


def connect_with_retry():
    max_attempts = 5
    delay = 1

    for attempt in range(1, max_attempts + 1):
        try:
            print(f"Connecting to PostgreSQL... attempt {attempt}")

            return psycopg.connect(
                host="postgres",
                port=5432,
                dbname="playground",
                user="postgres",
                password="postgres",
            )

        except OperationalError:
            if attempt == max_attempts:
                print("Failed to connect to PostgreSQL.")
                raise

            print(f"Connection failed. Retrying in {delay}s...")
            time.sleep(delay)
            delay *= 2


# def main():
#     with connect_with_retry() as conn:
#         with conn.cursor() as cur:
#             cur.execute("""
#                 CREATE TABLE IF NOT EXISTS orders (
#                     order_id INTEGER PRIMARY KEY,
#                     customer_id INTEGER NOT NULL,
#                     product TEXT NOT NULL,
#                     amount NUMERIC NOT NULL
#                 )
#             """)

#             with open("/data/orders.csv", newline="") as csv_file:
#                 reader = csv.DictReader(csv_file)

#                 for row in reader:
#                     cur.execute("""
#                         INSERT INTO orders (
#                             order_id,
#                             customer_id,
#                             product,
#                             amount
#                         )
#                         VALUES (%s, %s, %s, %s)
#                         ON CONFLICT (order_id) DO NOTHING
#                     """, (
#                         row["order_id"],
#                         row["customer_id"],
#                         row["product"],
#                         row["amount"],
#                     ))


# if __name__ == "__main__":
#     main()

def main():
    start = time.perf_counter()
    row_count = 0

    with psycopg.connect(
        host="postgres",
        port=5432,
        dbname="playground",
        user="postgres",
        password="postgres",
    ) as conn:

        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY,
                    customer_id INTEGER NOT NULL,
                    product TEXT NOT NULL,
                    amount NUMERIC NOT NULL
                )
            """)

            with open("/data/orders-large.csv", newline="") as csv_file:
                reader = csv.DictReader(csv_file)

                for row in reader:
                    cur.execute("""
                        INSERT INTO orders (
                            order_id,
                            customer_id,
                            product,
                            amount
                        )
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (order_id) DO NOTHING
                    """, (
                        row["order_id"],
                        row["customer_id"],
                        row["product"],
                        row["amount"],
                    ))

                    row_count += 1

    elapsed = time.perf_counter() - start

    print(f"Processed: {row_count} rows")
    print(f"Duration: {elapsed:.2f}s")
    print(f"Throughput: {row_count / elapsed:.0f} rows/sec")


if __name__ == "__main__":
    main()