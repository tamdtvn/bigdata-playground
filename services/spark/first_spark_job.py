from pyspark.sql import SparkSession
from pyspark.sql.functions import spark_partition_id

spark = (
    SparkSession.builder
    .appName("BigDataPlayground-Session17")
    .master("local[4]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

path = "/data/lake/cleaned/orders/orders.parquet"

df = spark.read.parquet(path)

print("\n=== DATASET ===")
print(f"Rows: {df.count()}")

print("\n=== PARTITIONS ===")
print(f"Processing partitions: {df.rdd.getNumPartitions()}")

print("\n=== ROWS PER PARTITION ===")

(
    df
    .withColumn("partition_id", spark_partition_id())
    .groupBy("partition_id")
    .count()
    .orderBy("partition_id")
    .show(100, truncate=False)
)

print("\n=== EXECUTION PLAN ===")

(
    df
    .filter(df.amount > 900)
    .select("amount")
    .explain("formatted")
)

spark.stop()