## Infrastructure Foundation

→ The Big Data Playground uses Docker as the foundation for isolated, reproducible environments.

→ Multiple services communicate through Docker networks.

→ Services should communicate using service names rather than hard-coded container IP addresses.

→ Docker Compose is used to define and orchestrate the local multi-container environment.


                 Docker
                    │
       ┌────────────┼────────────┐
       │            │            │
     Image      Container      Network
       │            │            │
       │       Dockerfile        │
       │            │            │
       └────────────┼────────────┘
                    │
               Compose
                    │
                    ▼
          Multi-container System

## Persistent Storage

Stateful services use Docker volumes for persistent data.

PostgreSQL data is stored in the `postgres_data` volume rather than being coupled directly to the PostgreSQL container lifecycle.   

## Pipeline Reliability

PostgreSQL exposes a Healthcheck using `pg_isready`.

The ingestion job waits for PostgreSQL to become healthy before starting.

The ingestion application also retries transient database connection
failures using Exponential Backoff.

This provides two layers of protection:

→ Infrastructure readiness: Healthcheck

→ Application resilience: Retry + Backoff


       Big Data Playground

       datasets/orders.csv
              │
              │ read-only bind mount
              ▼
       ┌───────────────────────┐
       │ Python Ingestion Job  │
       │                       │
       │ Retry + Backoff       │
       └──────────┬────────────┘
              │
              │ postgres:5432
              ▼
       ┌───────────────────────┐
       │ PostgreSQL            │
       │                       │
       │ Healthcheck           │
       └──────────┬────────────┘
              │
              ▼
       postgres-data
              Volume


## Ingestion Performance Review

Two ingestion strategies were evaluated using 100,000 records.

       | Strategy          |        Row-by-row INSERT |          PostgreSQL COPY |
       | ----------------- | -----------------------: | -----------------------: |
       | Row-by-row INSERT | 8.08s                    | 12,369 rows/sec          |
       | PostgreSQL COPY   | 0.10s                    | 988,933 rows/sec         |



       | Tiêu chí          |        Row-by-row INSERT |          PostgreSQL COPY |
       | ----------------- | -----------------------: | -----------------------: |
       | 100k rows         |                    8.08s |                    0.10s |
       | Throughput        |            12,369 rows/s |           988,933 rows/s |
       | Performance       |                 Thấp hơn |             ~80x cao hơn |
       | Failure isolation |                  Tốt hơn |                  Thô hơn |
       | Atomicity         | Tùy transaction strategy |                   Rất rõ |
       | Bad row           |    Có thể xử lý từng row | Có thể fail cả bulk load |
       | Complexity        |                 Đơn giản |         Cao hơn một chút |


PostgreSQL COPY provided approximately 80x higher throughput in this
experiment.

However, an intentional invalid record caused the COPY operation to fail
and the transaction to roll back completely.

No ingestion strategy has been selected as the final architecture yet.

Future design should consider:

- Performance
- Data Quality
- Failure Granularity
- Atomicity
- Maintainability
- Observability       

## Analytical Storage Experiment

CSV and Parquet are currently being evaluated for analytical workloads.

Initial 100K-row experiment:

- CSV: 2.54 MB
- Parquet: 0.62 MB
- CSV query: 0.067223s
- Parquet query: 0.430843s

Parquet demonstrated significant storage reduction and provides column pruning and data skipping capabilities.

However, the current experiment does not justify selecting Parquet based on query performance alone.

Further architectural decisions will depend on larger datasets and analytical access patterns.

## Analytical Data Partitioning

Analytical order data is partitioned by month:

`order_month=YYYY-MM`

This layout was selected based on measured daily, monthly, and yearly analytical workloads.

Monthly partitioning balances query pruning effectiveness with partition/file-management overhead.

See ADR-002 for evidence and rationale.

## Data Lake
Data Lake chủ yếu giải quyết: Storage decoupled from compute [Storage–Compute Decoupling].

                DATA PRODUCERS

       Application      IoT       Logs      APIs
              │            │          │         │
              └────────────┴────┬─────┴─────────┘
                                ▼
                     ┌─────────────┐
                     │             │
                     │  DATA LAKE  │
                     │             │
                     │ CSV         │
                     │ JSON        │
                     │ Parquet     │
                     │ Logs        │
                     │ ...         │
                     └──────┬──────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
       SQL            Spark            ML
       Analytics       Processing       Training

### Folder Structure

       data/
       ├── lake/
       │   ├── raw/
       │   │   └── orders/
       │   │       └── orders-partition.csv
       │   │
       │   ├── cleaned/
       │   │   └── orders/
       │   │       └── orders.parquet
       │   │
       │   └── curated/
       │       ├── daily_revenue/
       │       └── monthly_revenue/
       │
       └── experiments/
       ├── non_partitioned/
       ├── by_day/
       ├── by_month/
       ├── pushdown/
       └── pushdown_sorted/

### Data Lake Foundation

                    BUSINESS WORKLOAD
                           │
                           ▼
                       DATA LAKE
                           │
                           ▼
                        PARQUET
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         Partition      Row Groups    Columns
              │            │            │
              ▼            ▼            ▼
          Pruning       Skipping      Pruning
              │            │            │
              └────────────┼────────────┘
                           ▼
                    LESS DATA READ
                           │
                           ▼
                     PERFORMANCE
                           │
                           ▼
                    DATA KEEPS GROWING
                           │
                           ▼
                  SINGLE MACHINE LIMIT?
                           │
                    ┌──────┴──────┐
                    │             │
                   NO            YES
                    │             │
              keep simple     Scale Out?
                                  │
                                  ▼
                       DISTRIBUTED PROCESSING



## Processing Efficiency Principle

The system should avoid unnecessary work at every processing layer:

- Storage: avoid reading unnecessary data.
- Processing: avoid unnecessary computation.
- Distributed execution: avoid unnecessary data movement.
- Scheduling: avoid unnecessary parallel work.

**Process less. Move less. Coordinate less.**


## Distributed Reliability Principle

Reliability is not the absence of failure.

The system should contain failures and recover the smallest practical
unit of work at reasonable cost.

Partition design affects:

- parallelism
- scheduling overhead
- skew sensitivity
- recovery granularity


## Scaling Decision Principle

Distributed processing is not selected because data is "big."

Scaling decisions should start from business requirements and
quality attributes.

Decision order:

    Understand workload
        ↓
    Reduce unnecessary work
        ↓
    Measure against SLA
        ↓
    Optimize / reasonable Scale Up
        ↓
    Scale Out only when justified

Technology must justify itself by the problem it solves.