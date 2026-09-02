# Sprint 4 — Distributed Processing Foundations

## Session 16 — Why Distributed Processing?

### Goal

Understand the fundamental distributed-processing model before
introducing a framework such as Spark.

### Mental Model

Dataset
    ↓
Processing Partitions
    ↓
Tasks
    ↓
Workers
    ↓
Parallelism

### Key Concepts

- Processing Partition divides a dataset into independent work units.
- A Task processes one partition.
- Workers provide resources to execute tasks.
- Parallelism depends on available work units and execution resources.
- Too few partitions limit parallelism.
- Too many tiny partitions create scheduling and management overhead.
- Uneven partitions can cause Data Skew.

### Scaling Principle

Scale Out only after:

1. Unnecessary work has been reduced.
2. The single-machine design has been reasonably optimized.
3. Scale Up is insufficient or inappropriate.
4. Workload requirements still cannot be met.

### Key Insight

**More machines do not automatically mean more performance.**

Effective distributed processing requires enough independent work,
balanced partitions, useful parallelism, and reasonable coordination
overhead.

### Definition of Done

- [x] Understand Processing Partition
- [x] Understand Task
- [x] Understand Worker
- [x] Understand Parallelism
- [x] Distinguish storage partition from processing partition
- [x] Understand Data Skew
- [x] Understand partition granularity trade-off
- [x] Build a distributed-processing mental model without Spark

### Mental Model

Our mental model              Spark

Coordinator             →     Driver
                               │
Worker-side process      →     Executor
                               │
Processing Partition     →     Partition
                               │
Unit of work             →     Task
                               │
Parallel execution       →     Executors / cores


## Session 17 — Spark Fundamentals

### Goal

Map the distributed-processing mental model from Session 16 to Spark and verify it with a real Spark job.

### Mental Model

Application Intent
    ↓
Lazy Evaluation
    ↓
Optimizer
    ↓
Physical Plan
    ↓
Processing Partitions
    ↓
Tasks
    ↓
Execution

### Experiment

Dataset:

- 1,000,000 orders
- Parquet
- 10 Parquet Row Groups
- Spark local[4]

Observed:

- Spark processing partitions: 4
- Row distribution:
  - Partition 0: 300,000
  - Partition 1: 400,000
  - Partition 2: 300,000

### Key Evidence

10 Parquet Row Groups did not become 10 Spark partitions.

Therefore:

**Storage layout influences processing layout but does not dictate it 1:1.**

Execution plan for:

    filter(amount > 900)
    select(amount)

showed:

    PushedFilters:
    - IsNotNull(amount)
    - GreaterThan(amount, 900)

    ReadSchema:
    - amount

This provides direct evidence of:

- Predicate Pushdown
- Column Pruning

### Key Insights

- Transformations describe work; Actions demand results.
- Lazy Evaluation gives Spark an opportunity to optimize the complete intent.
- Spark partitions are processing units.
- Parquet Row Groups are storage units.
- Predicate Pushdown does not guarantee effective Data Skipping.
- Optimization often means eliminating unnecessary work.

### Definition of Done

- [x] Understand Driver and Executor responsibilities
- [x] Understand Transformation vs Action
- [x] Understand Lazy Evaluation
- [x] Inspect a Spark Physical Plan
- [x] Observe Spark processing partitions
- [x] Observe Column Pruning
- [x] Observe Predicate Pushdown
- [x] Distinguish Parquet Row Groups from Spark partitions