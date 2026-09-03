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


## Session 18 — Distributed Aggregation & Shuffle

### Goal

Understand why distributed aggregation may require data movement,
how Shuffle creates execution boundaries, and how Spark adapts
execution using runtime evidence.

### Problem

For:

    filter(amount > 900)

each processing partition can evaluate its rows independently.

For:

    GROUP BY product

the same product may exist across multiple partitions.

Related data must therefore meet before the final result can be produced.

### Mental Model

Input Partitions
    ↓
Partial Aggregation
    ↓
Shuffle
    ↓
Final Aggregation
    ↓
Result

### Experiment

Dataset:

- 1,000,000 orders
- 5 products
- Spark local[4]
- 4 input processing partitions

Filter plan:

    Scan parquet
        ↓
    ColumnarToRow
        ↓
    Filter

No redistribution of data was required.

Group By plan:

    Scan parquet
        ↓
    Partial HashAggregate
        ↓
    Exchange
        ↓
    Final HashAggregate

The Exchange provided evidence of a Shuffle.

### Partial Aggregation

Spark aggregated data locally before the Shuffle.

Observed shuffle statistics:

    rowCount = 15
    sizeInBytes = 480 B

This reduced approximately 1,000,000 input rows to only 15 partial
aggregation rows before data movement.

### Shuffle

Shuffle redistributes data between processing partitions so related
data can be processed together.

Principle:

**Shuffle happens when related data must meet.**

### Stage

Shuffle creates an execution boundary.

Conceptually:

    Stage 1
        ↓
    Shuffle
        ↓
    Stage 2

A Stage contains tasks that can execute without crossing the next
Shuffle boundary.

### Adaptive Query Execution

Initial plan:

    hashpartitioning(product, 200)

Runtime evidence:

    15 rows
    480 B

Final plan contained:

    AQEShuffleRead
    Arguments: coalesced

Spark therefore adapted the execution plan and coalesced small
shuffle partitions.

### Key Insights

- Filter can be processed independently by each partition.
- Group By may require related data from multiple partitions.
- Data movement can be more expensive than computation.
- Partial aggregation can dramatically reduce Shuffle traffic.
- Shuffle creates a new processing layout.
- Shuffle creates Stage boundaries.
- AQE can modify execution using runtime statistics.
- Too many tiny partitions create unnecessary scheduling overhead.

### Principles

**Reduce before you move.**

**Plan → Measure → Adapt.**

**Big Data performance is often less about processing faster
and more about avoiding unnecessary work.**

### Definition of Done

- [x] Understand why Group By may require Shuffle
- [x] Identify Exchange in a Spark Physical Plan
- [x] Understand Partial vs Final Aggregation
- [x] Understand Shuffle as data redistribution
- [x] Understand Shuffle as a Stage boundary
- [x] Observe runtime Shuffle statistics
- [x] Understand Adaptive Query Execution
- [x] Observe AQE coalescing small Shuffle partitions


## Session 19 — Failure & Parallelism

### Goal

Understand how distributed processing contains failures,
retries failed work, and reconstructs lost computation.

### Experiment

Dataset:

- 1,000,000 numbers
- 4 processing partitions
- Spark local[4,2]

Partition 1 was intentionally failed on its first attempt.

Observed final result:

    (0, 0, 250000)
    (1, 1, 250000)
    (2, 0, 250000)
    (3, 0, 250000)

Only Partition 1 required another attempt.

### Evidence

Partition 1:

    Attempt 0 → FAILED
    Attempt 1 → SUCCESS

Other partitions:

    Attempt 0 → SUCCESS

Completed work was not unnecessarily repeated.

### Recovery Model

Failure
    ↓
Identify failed work
    ↓
Classify failure
    │
    ├── Transient
    │      ↓
    │    Retry
    │
    └── Permanent
           ↓
         Fail / Escalate

### Lineage

Lineage describes how lost computation can be reconstructed
from previous data and transformations.

Conceptually:

    Source Partition
          ↓
    Transformation
          ↓
    Result Partition

If the result is lost, Spark can use the dependency information
to recompute the required work.

### Narrow vs Wide Dependency

Narrow Dependency:

    P0 → P0'
    P1 → P1'
    P2 → P2'

Work is mostly local to corresponding partitions.

Wide Dependency:

    P0 ─┐
    P1 ─┼──→ Output Partition
    P2 ─┤
    P3 ─┘

Multiple input partitions contribute to an output partition.

Wide dependencies commonly require Shuffle and make recovery
more complex.

### Partition as Recovery Boundary

Partitions affect more than parallelism.

    Partition
       ├── Parallelism
       └── Recovery Granularity

Large partitions may make failed work expensive to recompute.

Too many small partitions may create scheduling overhead.

Partition sizing is therefore a trade-off.

### Key Insights

- Worker/task failure does not necessarily mean Job failure.
- Recover at the smallest practical unit of failure.
- Retry is useful for transient failures.
- Retry does not solve permanent failures.
- Lineage enables reconstruction of lost computation.
- Narrow dependencies are easier to recover locally.
- Shuffle and wide dependencies increase recovery complexity.
- Partition design affects both performance and fault tolerance.

### Principles

**Recover at the smallest practical unit of failure.**

**Reliability is not the absence of failure; it is the ability
to contain and recover from failure at reasonable cost.**

### Definition of Done

- [x] Observe task-level retry
- [x] Understand Task Attempt
- [x] Understand Lineage
- [x] Distinguish transient and permanent failures
- [x] Understand Narrow Dependency
- [x] Understand Wide Dependency
- [x] Connect Shuffle to recovery complexity
- [x] Connect partition sizing to recovery granularity

### Mental Model

                  BUSINESS WORKLOAD
                         │
                         ▼
                  Quality Attributes
                         │
                         ▼
                   Data Layout
                         │
                         ▼
                 Process LESS data
                         │
                         ▼
                 Measure against SLA
                         │
              ┌──────────┴──────────┐
              │                     │
            PASS                   FAIL
              │                     │
              ▼                     ▼
           Keep it           Optimize / Scale Up
                                    │
                                    ▼
                              Still insufficient?
                                    │
                                   YES
                                    │
                                    ▼
                               SCALE OUT
                                    │
                                    ▼
                         Processing Partitions
                                    │
                                    ▼
                                  Tasks
                                    │
                                    ▼
                                 Workers
                                    │
                                    ▼
                              Parallelism
                                    │
                 ┌──────────────────┼──────────────────┐
                 ▼                  ▼                  ▼
              Shuffle             Skew              Failure
                 │                  │                  │
               Stage           Straggler            Retry
                 │                                     │
                AQE                                 Lineage



## Session 20 — Distributed Processing Decision Model

### Goal

Turn the Spark and distributed-processing concepts from Sprint 4
into an architectural decision model.

### Decision Model

    Business Requirement
        ↓
    Quality Attributes / SLA
        ↓
    Understand Workload
        ↓
    Reduce Unnecessary Work
        ↓
    Measure
        ↓
    Can reasonable Single Machine / Scale Up meet SLA?
        │
        ├── Yes → Keep Architecture Simple
        │
        └── No
            ↓
        Can workload parallelize effectively?
            │
            ├── No → Find another bottleneck
            │
            └── Yes
                ↓
            Scale Out
                ↓
        Distributed Processing
                ↓
            Measure Again

### Distributed Processing Costs

Scale Out introduces additional concerns:

- Shuffle and data movement
- Scheduling overhead
- Data skew
- Stragglers
- Coordination
- Failure and retry
- Operational complexity

Parallelism is therefore not free.

### Key Decision Principle

Data size alone does not justify distributed processing.

Before introducing distributed technology, identify the bottleneck
that the technology is expected to solve.

### Sprint 4 Mental Model

Dataset
    ↓
Processing Partitions
    ↓
Tasks
    ↓
Workers / Executors
    ↓
Parallelism
    │
    ├── Shuffle → Stage → AQE
    ├── Skew → Straggler
    └── Failure → Retry → Lineage

### Sprint 4 Principles

**Split work to gain parallelism.**

**Reduce before you move.**

**Recover at the smallest practical unit of failure.**

**Parallelism is not free.**

**Technology must justify itself by the problem it solves.**

### Definition of Done

- [x] Understand Processing Partition / Task / Worker
- [x] Understand Parallelism
- [x] Run a real Spark workload
- [x] Inspect Spark execution plans
- [x] Understand Shuffle and Stage
- [x] Observe Adaptive Query Execution
- [x] Understand Data Skew and Stragglers
- [x] Observe task-level retry
- [x] Understand Lineage and recovery
- [x] Understand Scale Up vs Scale Out
- [x] Build a distributed-processing decision model

## Sprint 4 Status

**COMPLETED**