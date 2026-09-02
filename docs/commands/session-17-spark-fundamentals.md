# Session 17 — Spark Fundamentals

## Run Spark Job

docker compose run --rm spark /opt/spark/bin/spark-submit /app/first_spark_job.py

## Important Debugging Tool

DataFrame.explain("formatted")

Use it to inspect how Spark plans to execute a query.