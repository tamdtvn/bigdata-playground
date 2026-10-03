# Sprint 6 — Real Workflow Orchestration

## Session 26 — Evaluate Orchestration Technologies

### Goal

Learn how to evaluate orchestration technologies from requirements,
constraints and evidence rather than popularity or feature count.

### Playground Requirements

Required orchestration capabilities:

- Dependency Management
- Scheduling
- State Tracking
- Retry
- Backfill
- Observability
- Local / Docker-friendly execution

A capability may be required without having the same decision weight as every other capability.

**Must-have determines eligibility. Weight determines preference.**

### Hard Constraints

The Playground must run locally using Docker Desktop.

A candidate that cannot satisfy a hard constraint is eliminated before weighted comparison.

        Candidate
            ↓
        Hard Constraints
            ↓
         Feasible?
         /     \
       NO        YES
        ↓         ↓
    Eliminate   Evaluate

### Feasibility vs Suitability

Feasibility:

    Can the solution work in our environment?

Suitability:

    Among feasible solutions, which best fits our requirements?

### Capability vs Complexity

More features do not automatically make a technology better.

Unused capabilities may introduce:

- configuration complexity
- operational complexity
- upgrade surface
- security surface
- learning cost
- troubleshooting cost

**Every capability has a complexity tax.**

### Build vs Adopt

Building a custom orchestrator may improve understanding but introduces
development and maintenance cost.

Once the underlying concepts are understood, adopting an existing tool
is preferable when rebuilding infrastructure provides little unique value.

### Ecosystem Maturity

Popularity alone is not sufficient evidence.

For long-lived systems evaluate:

- community
- documentation
- release stability
- maintenance activity
- integrations
- troubleshooting resources
- talent availability
- long-term viability

### Decision Framework

    Problem
       ↓
    Requirements
       ↓
    Hard Constraints
       ↓
    Candidate Filtering
       ↓
    Evaluation Criteria
       ↓
    Weights
       ↓
    Score + Reason + Evidence
       ↓
    Trade-offs
       ↓
    Decision
       ↓
    PoC / Experiment
       ↓
    Evidence
       ↓
    Validate Decision

### Principles

**Choose the simplest solution that adequately satisfies the requirements.**

**A hard constraint determines whether a solution is possible;
weighted criteria determine which possible solution is preferable.**

**Decision matrices support reasoning; evidence validates the decision.**

### Definition of Done

- [x] Define orchestration requirements
- [x] Distinguish must-have from decision weight
- [x] Understand Hard Constraints
- [x] Distinguish Feasibility from Suitability
- [x] Apply KISS and YAGNI to technology selection
- [x] Recognize Complexity Tax
- [x] Distinguish popularity from Ecosystem Maturity
- [x] Understand Weighted Decision Matrix
- [x] Connect architecture decisions to PoC evidence


## Session 27 — First Real DAG

### Goal
Convert the manual Raw → Cleaned → Curated pipeline into a real orchestrated DAG.

### Experiments

1. DAG with dependency:
   - `cleaned >> curated`
   - curated started only after cleaned succeeded.

2. DAG without dependency:
   - both tasks started at the same time.
   - confirmed code order is not execution order.

3. Real pipeline integration:
   - Airflow invoked real processing scripts.
   - Cleaned Parquet and curated revenue datasets were created.

### Evidence

Airflow:
- `build_cleaned_orders`: SUCCESS
- `build_revenue_curated`: SUCCESS

Data Lake:
- `orders.parquet`
- `daily_revenue.parquet`
- `monthly_revenue.parquet`

### Key Insights

- Code order != execution dependency.
- DAG dependencies define both waiting and possible parallelism.
- Airflow acts as the control plane.
- Processing jobs act as the data plane.
- Task success is execution evidence, not full proof of data correctness.

### Principle

**Move execution knowledge from humans into machine-readable dependencies.**

### Definition of Done

- [x] Airflow runs locally
- [x] First DAG created
- [x] Dependency execution observed
- [x] Parallel execution observed without dependency
- [x] Real processing integrated
- [x] Real Data Lake outputs created
- [x] Control Plane vs Data Plane understood


## Session 28 — Scheduling, Retry & Backfill

### Goal

Validate Airflow scheduling, task-level retry, and historical backfill through controlled experiments.

### Experiments & Evidence

**1. Scheduling**

- Changed the main DAG schedule from `None` to `*/5 * * * *`.
- Airflow automatically created scheduled DAG Runs without manual triggering.
- Confirmed that scheduling responsibility moved from the human operator to Airflow.

**2. Retry**

- Added a test task that intentionally failed on its first attempt.
- Configured `retries=2` and a 10-second retry delay.
- The task succeeded on its second attempt.
- Downstream processing tasks continued, and the DAG Run completed successfully.

**3. Backfill**

- Created a separate `backfill_experiment` DAG with a daily schedule.
- Requested a backfill for September 8–10, 2026.
- Airflow created three independent historical DAG Runs:

  - `backfill__2026-09-08T00:00:00+00:00`
  - `backfill__2026-09-09T00:00:00+00:00`
  - `backfill__2026-09-10T00:00:00+00:00`

- Each run had its own task instance and execution logs.
- In the observed backfill runs, `data_interval_start` and `data_interval_end` were both equal to the corresponding logical date.

### Architectural Findings

- Scheduling, retry, and backfill are orchestration capabilities.
- Safe retry requires idempotent processing.
- The current processing scripts are not data-interval-aware: historical runs would still process the entire dataset.
- A future processing contract should explicitly identify the business date or data interval to process.
- Partition-scoped outputs can limit the amount of work required for retry and backfill.
- Atomic publishing is needed to protect existing valid outputs during replacement.

### Proposed Design — Not Yet Implemented

```text
Airflow DAG Run
    ↓
Explicit Business Date
    ↓
Date-aware Processing
    ↓
Validate
    ↓
Atomic Publish
    ↓
Curated/date=YYYY-MM-DD/
```

### Key Principle

**Orchestration can retry or backfill work, but processing must understand the correct business scope and support safe re-execution.**

### Definition of Done

- [x] Automatic scheduling demonstrated.
- [x] Task-level retry demonstrated.
- [x] Three independent historical DAG Runs created.
- [x] Temporal execution behavior observed in logs.
- [x] Processing contract limitation identified.
- [x] Partition-scoped publishing design discussed.
- [ ] Date-aware processing implemented (future work).
- [ ] Atomic publishing implemented and tested (future work).

## Session 29 — Failure, State & Observability

### Goal

Learn how execution state and diagnostic evidence help localize a pipeline failure before investigating its root cause.

### Experiment

Created a controlled Airflow DAG:

```text
extract_data
    ↓
transform_data
    ↓
publish_data
```

`extract_data` intentionally raised:

```text
FileNotFoundError:
/lake/raw/ilostat/input.csv does not exist
```

The task was configured with:

```text
retries = 2
```

### Prediction

- `extract_data` would execute three attempts.
- After retry exhaustion, `extract_data` would fail.
- Downstream tasks would not execute because their upstream dependency did not succeed.
- Investigation should start by localizing the failed task before reading detailed logs.

### Evidence

Observed DAG state:

```text
DAG Run             FAILED

extract_data         FAILED
    Try Number       3

transform_data       UPSTREAM FAILED
    Try Number       0

publish_data         UPSTREAM FAILED
    Try Number       0
```

The final `extract_data` attempt reported:

```text
Try number: 3

FileNotFoundError:
/lake/raw/ilostat/input.csv does not exist
```

### Evidence Ladder

```text
DAG FAILED
    ↓
Which task failed?
    ↓
extract_data
    ↓
How many attempts?
    ↓
3
    ↓
What happened?
    ↓
FileNotFoundError
    ↓
Which resource?
    ↓
/lake/raw/ilostat/input.csv
    ↓
Root Cause
Expected input file does not exist
```

### Findings

`FAILED` and `UPSTREAM FAILED` represent different situations:

```text
FAILED
→ The task executed and failed.

UPSTREAM FAILED
→ The task did not execute because an upstream dependency failed.
```

Retry history also provides diagnostic evidence. Repeated identical failures may indicate a deterministic or permanent problem, although this must still be verified.

### Mental Model

```text
Something is wrong
        ↓
State
        ↓
Failure Location
        ↓
Attempts
        ↓
Logs
        ↓
Verify Evidence
        ↓
Root Cause
```

### Key Principles

**Localize the failure before diagnosing the cause.**

**Observability reduces the search space between symptom and cause.**

**Retry is a recovery mechanism, not a repair mechanism.**

### Definition of Done

- [x] Permanent failure created intentionally.
- [x] Retry exhaustion observed.
- [x] Three attempts verified.
- [x] Failure propagation observed.
- [x] `FAILED` vs `UPSTREAM FAILED` distinguished.
- [x] Failure localized from DAG → Task → Attempt → Log.
- [x] Root cause identified from evidence.

**Status:** Session 29 completed.