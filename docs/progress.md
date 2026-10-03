# BIG DATA SANDBOX PROGRESS

## = 2026-08-01
Sprint 0
└── Project Foundation

Completed
- Repository
- Folder structure
- Git Ignore
- README

Lessons Learned
- Repository should be organized before coding.



## = 2026-08-16

### Sprint 1: 5 sessions

Sprint 1 – Docker Foundation
│
├── Session 1
│   └── Environment & Reproducibility
│
├── Session 2
│   └── Image vs Container
│
├── Session 3
│   └── Dockerfile, Layers & Cache
│
├── Session 4
│   └── Build Context & .dockerignore
│
└── Session 5
    └── Docker Network & Compose



## = 2026-08-16

### Sprint 2: 5 sessions

Sprint 2 – Data Engineering Foundation
│
├── Session 6
│   └── PostgreSQL & Persistent Storage
│
├── Session 7
│   └── Port Publishing & System Boundaries
│
├── Session 8
│   └── First Data Pipeline
│
├── Session 9
│   └── Pipeline Reliability
│
└── Session 10
    └── Architecture Review & Ingestion Performance



## = 2026-08-22

### Sprint 3: 5 sessions

Sprint 3 — Data Storage & Processing Foundations
│
├── Session 11
│   └── CSV vs Parquet
│
├── Session 12
│   └── Partitioning
│
├── Session 13
│   └── Predicate Pushdown & Data Skipping
│
├── Session 14
│   └── Data Lake Foundations
│
└── Session 15
    └── Sprint Review & Scaling Foundations   



## = 2026-08-31    

### Sprint 4 — Distributed Processing Foundations

Session 16 — Why Distributed Processing?
             Partition → Task → Worker

Session 17 — Spark Fundamentals
             Driver / Executor / Job / Stage / Task

Session 18 — Distributed Aggregation
             Shuffle

Session 19 — Failure & Parallelism
             Retry / Partition / Worker Failure

Session 20 — Sprint Review
             Single Machine vs Distributed Processing



### SPRINT 5 — DATA PIPELINE ORCHESTRATION

Session 21 — Why Orchestration?
             Manual Pipeline → Dependency Problem

Session 22 — DAG Fundamentals
             Task → Dependency → Upstream / Downstream

Session 23 — Scheduling & Idempotency
             Retry → Backfill → Rerun

Session 24 — Pipeline State & Observability
             Success → Failed → Running → History

Session 25 — Sprint Review
             From Scripts → Reliable Data Pipeline


### SPRINT 6 — REAL WORKFLOW ORCHESTRATION

Session 26 — Our Requirements → Evaluate Orchestration Technologies

Session 27 — First Real DAG

Session 28 — Scheduling + Retry + Backfill Experiment

Session 29 — Failure + State + Observability Experiment

Session 30 — Architecture Review
             Manual Pipeline → Production-like Data Platform


# Big Data Playground — Final Status

**Status:** COMPLETED

## Completed Learning Areas

### Data Ingestion
- Containerized ingestion.
- PostgreSQL connectivity.
- Idempotent ingestion.
- Bulk loading with COPY.
- Reliability and readiness.
- Failure granularity and atomicity.

### Analytical Storage
- CSV vs Parquet.
- Columnar storage.
- Row groups.
- Column pruning.
- Predicate pushdown.
- Data skipping.
- Partition pruning.
- Workload-aware partitioning.

### Data Lake
- Raw / Cleaned / Curated zones.
- Source truth preservation.
- Data validation.
- Data contracts.
- Data products.
- Reprocessability.

### Distributed Processing
- Scale Up vs Scale Out.
- Processing partitions.
- Tasks and workers.
- Spark Driver and Executors.
- Lazy evaluation.
- Shuffle and stages.
- Data skew.
- Retry and lineage.
- Recovery granularity.

### Workflow Orchestration
- DAGs and dependencies.
- Scheduling.
- Execution state.
- Retry.
- Backfill.
- Failure propagation.
- Failure localization.
- Execution history and observability.
- Control Plane vs Data Plane.

### Architecture Decision Making
- Quality Attributes.
- Baselines and measurement.
- Architectural trade-offs.
- Technology hypotheses.
- PoC validation.
- Decision context.
- Evidence-based ADRs.

## Architecture Decisions

- ADR-001 — Repository Structure
- ADR-002 — Monthly Partitioning
- ADR-003 — Apache Airflow for Playground Orchestration

### Final Decision Model

```mermaid
flowchart LR
    A["Problem"] --> B["Requirements"]
    B --> C["Quality Attributes"]
    C --> D["Options"]
    D --> E["Trade-offs"]
    E --> F["Experiment"]
    F --> G["Evidence"]
    G --> H["Decision"]