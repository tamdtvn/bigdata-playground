import time
import psycopg


def main():
    start = time.perf_counter()

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

            with open("/data/orders-large-invalid.csv", "r") as csv_file:
                next(csv_file)  # skip CSV header

                with cur.copy("""
                    COPY orders (
                        order_id,
                        customer_id,
                        product,
                        amount
                    )
                    FROM STDIN
                    WITH (FORMAT CSV)
                """) as copy:
                    while data := csv_file.read(1024 * 1024):
                        copy.write(data)

    elapsed = time.perf_counter() - start

    print(f"Duration: {elapsed:.2f}s")
    rows = 100_000
    print(f"Throughput: {rows / elapsed:.0f} rows/sec")

if __name__ == "__main__":
    main()