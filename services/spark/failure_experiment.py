from pyspark.sql import SparkSession
from pyspark import TaskContext


spark = (
    SparkSession.builder
    .appName("BigDataPlayground-Session19")
    .master("local[4,2]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")


def process_partition(iterator):
    context = TaskContext.get()

    partition_id = context.partitionId()
    attempt = context.attemptNumber()

    print(
        f"Partition={partition_id}, "
        f"Attempt={attempt}"
    )

    # Intentionally fail partition 1 on its first attempt.
    if partition_id == 1 and attempt == 0:
        raise RuntimeError(
            "Intentional transient failure"
        )

    count = sum(1 for _ in iterator)

    yield partition_id, attempt, count


rdd = spark.sparkContext.parallelize(
    range(1_000_000),
    4
)

result = (
    rdd
    .mapPartitions(process_partition)
    .collect()
)

print("\n=== FINAL RESULT ===")

for row in sorted(result):
    print(row)

spark.stop()