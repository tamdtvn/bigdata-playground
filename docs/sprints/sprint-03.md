# Sprint 3 — Data Storage & Processing Foundations

## Session 11 — CSV vs Parquet

### Goal

Understand why analytical systems often use columnar storage
formats such as Parquet instead of CSV.

### Experiment

Dataset:
- 100,000 orders

CSV:
- Size: 2.54 MB

Parquet:
- Size: 0.62 MB
- Compression: Snappy
- Row groups: 4
- Row group size: 25,000 rows

### Concepts Learned

- Columnar Storage
- Schema
- Metadata
- Row Groups
- Column Pruning
- Data Skipping
- Crossover Point

### Query Experiment

Query:

SELECT amount
FROM orders
WHERE order_id > 80000;

Expected:
- Row Groups 1–3 skipped
- Row Group 4 considered
- order_id and amount required
- 20,000 rows returned

Result:

Parquet:
- Rows: 20,000
- Duration: 0.430843s

CSV:
- Rows: 20,000
- Duration: 0.067223s

### Observation

For this small dataset, CSV was significantly faster than Parquet.

Parquet reduced storage size by about 76%, but its query
overhead outweighed its optimization benefits at this scale.

### Key Insight

Parquet is not automatically faster than CSV.

Its advantages depend on:

- data size
- query pattern
- columns accessed
- row-group organization
- engine/runtime overhead

Architectural decisions should be based on workload and evidence,
not technology reputation.

### Mental Model

Don't process data you don't need.

Data Skipping → avoid unnecessary row groups.

Column Pruning → avoid unnecessary columns.

### Definition of Done

- [x] Convert CSV to Parquet
- [x] Inspect Parquet schema
- [x] Inspect Parquet metadata
- [x] Understand Row Groups
- [x] Experiment with Data Skipping
- [x] Experiment with Column Pruning
- [x] Compare CSV and Parquet query behavior
- [x] Record architectural observations



## Session 12 — Partitioning

### Goal

Understand how physical data partitioning affects analytical
query performance and operational overhead.

### Business Workload

Common queries:

- Daily revenue
- Monthly revenue
- Compare revenue between months
- Occasional yearly revenue

### Dataset

- 1,000,000 orders
- Dates distributed across 2026
- Deterministic generation using a fixed random seed

### Data Layouts

Three layouts were evaluated:

1. Non-partitioned — 1 partition
2. By month — 12 partitions
3. By day — 365 partitions

### Layout Creation Cost

| Layout | Partitions | Duration |
| --- | ---: | ---: |
| Non-partitioned | 1 | 0.236s |
| By Month | 12 | 0.591s |
| By Day | 365 | 4.726s |

### Query Results

| Workload | Non-partitioned | By Month | By Day |
| --- | ---: | ---: | ---: |
| Daily | 0.030599s | 0.008411s | 0.004164s |
| Monthly | 0.043685s | 0.007643s | 0.054943s |
| Yearly | 0.026792s | 0.024896s | 0.571435s |

All layouts returned identical row counts and revenue,
confirming query correctness.

### Observations

Daily partitioning produced the fastest daily query.

However:

- Monthly queries became slower.
- Yearly queries became significantly slower.
- Partition count increased from 12 to 365.
- Layout creation became significantly more expensive.

Monthly partitioning provided balanced performance across
daily, monthly, and yearly workloads.

### Key Insights

Partitioning does not make queries faster by itself.

Partition Pruning creates the performance benefit.

The benefit depends on query selectivity and must outweigh
partition/file-management overhead.

Too-fine partitioning can create a Small Files Problem.

### Decision

Use monthly partitioning for the current Playground analytical
orders workload.

Partition key:

`order_month=YYYY-MM`

See ADR-002.

### Definition of Done

- [x] Understand Partitioning
- [x] Compare partition granularities
- [x] Observe Partition Pruning
- [x] Observe Small Files Problem
- [x] Benchmark daily workload
- [x] Benchmark monthly workload
- [x] Benchmark yearly workload
- [x] Evaluate trade-offs
- [x] Select partition strategy
- [x] Record architectural decision