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


## Session 13 — Predicate Pushdown & Data Skipping

### Goal

Understand how query predicates interact with physical Parquet layout.

### Experiment

Used the same 1,000,000-order dataset with 10 Parquet row groups.

Two predicates were compared:

- `order_id > 900000`
- `amount > 900`

The original data was physically ordered by `order_id`.

Row-group statistics showed:

- `order_id` ranges were separated across row groups.
- `amount` ranges overlapped across all row groups.

### Initial Benchmark

| Predicate | After Read | Pushdown |
| --- | ---: | ---: |
| order_id > 900000 | 0.062166s | 0.006015s |
| amount > 900 | 0.028452s | 0.027473s |

`order_id` allowed 9 of 10 row groups to be skipped.

`amount` could not eliminate row groups because its values were
distributed across all row groups.

### Physical Ordering Experiment

The same dataset was sorted by `amount` and rewritten with the same
10-row-group layout.

This changed row-group statistics:

- `amount` became strongly separated between row groups.
- `order_id` became distributed across row groups.

### Second Benchmark

| Predicate | After Read | Pushdown |
| --- | ---: | ---: |
| order_id > 900000 | 0.068777s | 0.021306s |
| amount > 900 | 0.028382s | 0.006205s |

### Key Insights

Predicate Pushdown does not automatically produce Data Skipping.

Effective Data Skipping depends on the relationship between:

- Query predicates
- Physical data layout
- Data distribution
- Row-group statistics

Physical ordering can improve one access pattern while making another
less efficient.

### Principle

**Design data layout from access patterns, not from technology.**

### Definition of Done

- [x] Understand Predicate Pushdown
- [x] Understand Row Group Statistics
- [x] Observe effective and ineffective Data Skipping
- [x] Compare Filter After Read vs Pushdown
- [x] Change physical ordering
- [x] Observe query-performance impact
- [x] Connect physical layout to query workload

## Session 14 — Data Lake Foundations

### Goal

Understand why a Data Lake exists and implement a minimal data lifecycle.

### Architecture

data/
├── lake/
│   ├── raw/
│   │   └── orders/
│   ├── cleaned/
│   │   └── orders/
│   └── curated/
│       ├── daily_revenue/
│       └── monthly_revenue/
└── experiments/

### Pipeline

Raw Orders
    ↓
Validate + Clean + Convert
    ↓
Cleaned Orders
    ↓
Aggregate
    ├── Daily Revenue
    └── Monthly Revenue

### Evidence

Raw:
- 1,000,000 orders

Cleaned:
- 1,000,000 validated orders in Parquet

Curated:
- 365 daily revenue rows
- 12 monthly revenue rows

Invalid `amount=ABC` was rejected before reaching the Cleaned zone.

The original Raw data remained available for reprocessing.

### Key Insights

- Raw preserves source truth.
- Cleaned contains trusted data.
- Curated serves specific business needs.
- Data Contracts protect trust boundaries.
- Keeping Raw data enables reprocessing.
- Failed processing can leave stale previous outputs.
- Atomic Publish can prevent consumers from seeing incomplete output.

### Principle

**Preserve source truth, validate before trust, publish only valid data.**

### Definition of Done

- [x] Understand Data Lake purpose
- [x] Understand Storage–Compute Decoupling
- [x] Implement Raw / Cleaned / Curated zones
- [x] Implement Raw → Cleaned transformation
- [x] Implement Cleaned → Curated transformation
- [x] Test invalid data
- [x] Demonstrate Data Contract enforcement
- [x] Understand Reprocessability
- [x] Identify stale-output risk

### Data FLow Processing BEFORE Scale Out

    Business Workload
        ↓
    Data Lake / Data Zones
        ↓
    Choose efficient format
        ↓
    Organize physical layout
        ↓
    Partition Pruning + Data Skipping + Column Pruning + Predicate Pushdown
        ↓
    Process less data
        ↓
    Measure against SLA
        ↓
    Optimize / Scale Up
        ↓
    Still insufficient
        ↓
    Scale Out

    Summary: Workload → Layout → Less Work → Measure → Scale only when necessary.


## Session 15 — Sprint Review & Scaling Foundations

### Goal

Understand when increasing data volume becomes a distributed-processing problem rather than an optimization problem.

### Scaling Decision Model

    Business Workload
        ↓
    Optimize Data Layout
        ↓
    Process Less Data
        ↓
    Measure Against SLA
        ↓
    Scale Up if sufficient
        ↓
    Still insufficient?
        ↓
    Scale Out

### Key Insights

- Large data does not automatically require distributed processing.
- Reduce unnecessary work before adding compute.
- Scale Up is simpler than Scale Out and should be considered first.
- Scale Out introduces distributed-system complexity.
- Distributed processing becomes justified when an optimized
  single-machine solution can no longer satisfy workload requirements.

### Principle

**Before adding compute, reduce unnecessary work.**

Or:

**Workload → Layout → Less Work → Measure → Scale only when necessary.**

### Definition of Done

- [x] Understand Scale Up
- [x] Understand Scale Out
- [x] Understand why Scale Out adds complexity
- [x] Connect scaling decisions to workload and SLA
- [x] Identify when distributed processing becomes justified   


## Sprint 3 — Data Storage & Processing Foundations ✅

Completed:

- CSV vs Parquet
- Column Pruning
- Row Groups
- Partitioning
- Partition Pruning
- Predicate Pushdown
- Data Skipping
- Physical Ordering
- Data Lake Foundations
- Raw / Cleaned / Curated zones
- Data Contracts
- Reprocessability
- Scale Up vs Scale Out

### Sprint Principle

**Workload → Layout → Less Work → Measure → Scale only when necessary.**