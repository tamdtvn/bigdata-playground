from pyspark.sql import SparkSession
from pyspark.sql.functions import sum as spark_sum

spark = (
    SparkSession.builder
    .appName("BigDataPlayground-Session18")
    .master("local[4]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

path = "/data/lake/cleaned/orders/orders.parquet"

df = spark.read.parquet(path)

print("\n=== INPUT ===")
print(f"Input partitions: {df.rdd.getNumPartitions()}")

# --------------------------------------------------
# Experiment A — Filter
# --------------------------------------------------

filter_query = (
    df
    .filter(df.amount > 900)
    .select("product", "amount")
)

print("\n=== FILTER PLAN ===")
filter_query.explain("formatted")


# --------------------------------------------------
# Experiment B — Group By
# --------------------------------------------------

group_query = (
    df
    .groupBy("product")
    .agg(
        spark_sum("amount").alias("revenue")
    )
)

print("\n=== GROUP BY PLAN ===")
group_query.explain("formatted")


print("\n=== GROUP BY RESULT ===")

group_query.orderBy("product").show(
    truncate=False
)

spark.stop()