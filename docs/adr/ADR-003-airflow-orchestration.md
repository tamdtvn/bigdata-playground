# ADR-003 — Use Apache Airflow for Workflow Orchestration

## Status

Accepted

## Context

The Big Data Playground initially executed data processing jobs manually.

The processing pipeline itself worked, but execution knowledge remained with the human operator:

- dependency order;
- scheduling;
- execution state;
- retry;
- historical re-execution;
- failure investigation.

As the number of jobs and dependencies grows, manual coordination becomes increasingly difficult and error-prone.

The orchestration solution was expected to support:

- dependency management;
- scheduling;
- state tracking;
- retry;
- backfill;
- observability;
- local Docker-based development.

Apache Airflow, Prefect and Dagster were considered as orchestration candidates.

Airflow was selected as the technology hypothesis for the Playground PoC because it provided a clear workflow model and matched the batch-oriented learning scenario.

## Evidence

The hypothesis was validated through Sessions 27–29.

### Dependency Management

A real Raw → Cleaned → Curated pipeline was expressed as an Airflow DAG.

```text
build_cleaned_orders
        ↓
build_revenue_curated
```

The downstream task executed only after its upstream dependency completed successfully.

Removing the dependency allowed the tasks to execute concurrently, demonstrating that DAG dependencies define execution constraints rather than Python source-code order.

### Scheduling

A scheduled DAG automatically created executions without manual triggering.

### Retry

An intentional transient failure failed on its first attempt and succeeded on retry.

### Backfill

A historical backfill request for September 8–10, 2026 created three independent DAG Runs.

### State and Observability

A permanent failure demonstrated:

```text
extract_data       → FAILED
transform_data     → UPSTREAM FAILED
publish_data       → UPSTREAM FAILED
```

The failure could be localized through:

```text
DAG Run
 ↓
Task
 ↓
Attempt
 ↓
Log
 ↓
Root Cause
```

### Local Development

Airflow 3.3.1 successfully ran in the Playground Docker environment.

## Decision

Use Apache Airflow as the workflow orchestration technology for the Big Data Playground.

Airflow owns orchestration concerns:

```text
Dependency
Scheduling
State
Retry
Backfill
Execution History
Observability
```

Processing jobs continue to own:

```text
Read
Validate
Transform
Aggregate
Write
```

This preserves the separation between the orchestration control plane and the processing data plane.

## Consequences

### Positive

- Workflow dependencies become machine-readable.
- Scheduling no longer depends on manual execution.
- Task-level state and execution history are available.
- Transient failures can be retried automatically.
- Historical executions can be represented independently.
- Failure localization becomes easier.
- Processing code remains separated from orchestration concerns.

### Negative

Airflow introduces additional infrastructure and operational cost.

Production deployment may require additional concerns such as:

- deployment and upgrade management;
- metadata persistence;
- authentication and authorization;
- monitoring;
- availability;
- resource consumption.

These costs are intentionally not explored deeply in the Playground.

## Limitations

Airflow capability does not automatically make the complete pipeline reliable.

The current Playground still has known gaps:

- processing jobs are not business-date aware;
- backfill correctness at the business-data level has not been demonstrated;
- atomic publishing has not been implemented;
- production authentication has not been implemented;
- production monitoring and alerting have not been implemented;
- high availability has not been evaluated.

These are deliberately deferred until a real requirement justifies them.

## ILOSTAT Decision Boundary

This ADR accepts Airflow for the **Big Data Playground**.

It does **not** automatically select Airflow for ILOSTAT.

Airflow becomes an initial orchestration candidate for ILOSTAT.

The decision must be reevaluated against actual ILOSTAT requirements, including:

- number of jobs;
- dependency complexity;
- execution frequency;
- backfill requirements;
- operational constraints;
- infrastructure cost;
- reliability requirements.

For a small MVP with one source, one country and only a few weekly jobs, a simpler solution may be preferable if coordination complexity does not justify running an orchestrator.

## Decision Principle

**Technology decisions are contextual, not transferable by default.**

A technology should be adopted when the problem it solves justifies the cost it introduces.

```text
              ORCHESTRATION
                    │
       ┌────────────┼─────────────┐
       │            │             │
  Dependency     Scheduling     State
       │            │             │
       ├── Retry ───┤             │
       │            ├── Backfill  │
       │            │             │
       └────────────┴─────┬───────┘
                          │
                    Observability
```