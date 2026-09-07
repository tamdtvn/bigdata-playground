# Sprint 5 — Data Pipeline Orchestration

## Session 21 — Why Orchestration?

### Goal

Understand when a collection of scripts becomes an orchestration problem.

### Starting Point

Current playground pipeline:

    Raw
     ↓
    Cleaned
     ↓
    Curated

Executed manually by the developer.

### Execution Dependency

A downstream task should run only when its required upstream work
has completed successfully.

Example:

    cleaned_orders
         ↓
    daily_revenue

`cleaned_orders` is upstream.
`daily_revenue` is downstream.

### DAG

Pipeline dependencies form a graph of tasks.

A valid workflow dependency graph is typically:

- Directed
- Acyclic
- Graph

Example:

        cleaned
        /     \
       /       \
    revenue   customer
       \       /
        \     /
         report

Cycles are invalid because tasks may wait on each other indefinitely.

### Parallelism from Dependencies

Independent downstream branches can execute concurrently.

Sequential execution:

    5 + 3 + 10 + 20 + 30 + 5 = 73 min

Dependency-aware execution:

    5 + 3 + 10 + max(20, 30) + 5 = 53 min

The dependency model therefore supports both correctness and parallelism.

### Failure Propagation

If an upstream task fails:

    cleaned_orders FAILED
         ↓
    dependent tasks BLOCKED

Downstream tasks should not consume missing or invalid output.

### Recovery

If one independent branch fails, successful branches should not
be unnecessarily rerun.

Principle reused from distributed processing:

**Recover at the smallest practical unit of failure.**

### Orchestrator vs Processor

Processor:

    Spark / Python / SQL
    → performs computation

Orchestrator:

    coordinates jobs
    → what runs
    → when it runs
    → what it depends on
    → what happens after failure

### Key Insights

- A pipeline becomes a dependency graph, not merely a list of scripts.
- Dependency determines execution order.
- Dependency also reveals safe parallelism.
- Failure should propagate only to dependent downstream work.
- Successful independent work should be preserved.
- Manual execution is acceptable while coordination remains simple.

### Principle

**Introduce orchestration when coordination complexity exceeds the
benefit of manual simplicity.**

### Definition of Done

- [x] Understand execution dependency
- [x] Understand upstream and downstream
- [x] Understand why workflows form a DAG
- [x] Understand why cycles are invalid
- [x] Connect dependency to parallel execution
- [x] Connect failure propagation to recovery
- [x] Distinguish orchestrator from processor


## Session 22 — DAG Fundamentals

### Goal

Understand how a DAG becomes executable through dependencies, task states, valid execution ordering and critical-path reasoning.

### Task States

A workflow task may conceptually move through states such as:

    WAITING
        ↓
    READY
        ↓
    RUNNING
        ↓
    SUCCESS / FAILED

A task becomes READY when its required upstream dependencies have successfully completed.

### Fan-out

One task enables multiple independent downstream branches.

        A
      / | \
     B  C  D

### Fan-in

Multiple upstream branches must complete before one downstream task runs.

    B ─┐
    C ─┼── F
    D ─┘

### Declarative Dependencies

Instead of hard-coding:

    run A
    run B

declare:

    B depends on A

The execution engine can then infer readiness, waiting, failure propagation and safe parallel execution.

### Topological Order

A topological order is any sequential ordering that respects all dependency edges.

For the DAG:

        A
       / \
      B   C
      │   │
      D   E
       \ /
        F

Both can be valid:

    A, B, C, D, E, F
    A, C, B, E, D, F

A topological order does not mean the workflow must execute sequentially.

Independent tasks may execute concurrently.

### Critical Path

The Critical Path is the longest dependency path that determines the minimum possible workflow completion time.

Example:

    A = 5
    B = 20
    C = 2
    D = 30
    E = 4
    F = 5

Paths:

    A → B → D → F = 60 min
    A → C → E → F = 16 min

Critical Path:

    A → B → D → F

Minimum ideal workflow duration:

    60 minutes

### Optimization Principle

Optimizing work outside the Critical Path may not improve overall workflow completion time.

**Optimize the work that actually constrains completion.**

### Key Insights

- Dependencies determine when tasks become runnable.
- DAGs enable safe workflow parallelism.
- Fan-out creates independent branches.
- Fan-in synchronizes branches.
- A DAG may have multiple valid topological orders.
- Topological order is not the same as parallel execution.
- Critical Path must follow actual dependency edges.
- The longest dependency path determines ideal completion time.

### Definition of Done

- [x] Understand task readiness
- [x] Understand Fan-out and Fan-in
- [x] Understand declarative dependencies
- [x] Understand Topological Order
- [x] Distinguish execution ordering from parallelism
- [x] Understand Critical Path
- [x] Apply Critical Path to optimization decisions


## Session 23 — Scheduling, Idempotency & Backfill

### Goal

Understand how recurring pipelines safely process time-based data,
recover failed intervals and support historical reprocessing.

### Execution Time vs Data Interval

Execution Time:

    When a pipeline run is executed.

Data Interval:

    The logical time range of data processed by that run.

Duration:

    How long the execution takes.

Example:

    Execution Time:
        2026-09-08 01:00

    Data Interval:
        2026-09-07 00:00
        →
        2026-09-08 00:00

### Backfill

Backfill means running a pipeline for a past data interval that is
missing or needs rebuilding.

Example:

    Sep 6  SUCCESS
    Sep 7  SUCCESS
    Sep 8  FAILED
    Sep 9  SUCCESS

Later:

    Backfill Sep 8

Only the required historical interval should be rebuilt.

### Idempotency

A task is idempotent when repeated execution for the same logical
input does not corrupt or duplicate the logical result.

Conceptually:

    Run once  → correct result
    Run again → same correct result

Retry therefore requires safe re-execution.

### Retry and Idempotency

    Failure
       ↓
    Retry
       ↓
    Safe Re-execution
       ↓
    Idempotency

Without idempotency, retry may create duplicate or incorrect data.

### Partition-based Rebuild

For daily revenue:

    daily_revenue/
        date=2026-09-07/
        date=2026-09-08/
        date=2026-09-09/

A failed interval can be rebuilt independently:

    Rebuild date partition
           ↓
        Validate
           ↓
    Replace / Publish

This provides a simple recovery boundary.

### Atomic Publish

A safer processing pattern is:

    Process
       ↓
    Write temporary output
       ↓
    Validate
       ↓
    Publish only on success

Consumers should see either the previous valid output or the new
complete valid output, not partially written data.

### Concurrent Runs

Two runs processing the same logical data interval may cause:

- duplicate work
- duplicate data
- conflicting writes
- wasted CPU / memory
- race conditions

Concurrency therefore requires an explicit execution policy.

### Reliability Model

    Failure
       ↓
    Retry
       ↓
    Idempotent Re-execution
       ↓
    Validate
       ↓
    Atomic Publish
       ↓
    Reliable Output

### Key Insights

- Execution time and data interval are different concepts.
- Backfill rebuilds historical logical intervals.
- Retry is only safe when re-execution is safe.
- Idempotency is a foundation of reliable pipelines.
- Time partitions create useful recovery boundaries.
- Concurrent runs can introduce race conditions.
- Scheduling is more than simply triggering jobs by clock time.

### Principles

**Retry safely.**

**Recover the smallest required data interval.**

**Validate before trust and publish only valid output.**

### Definition of Done

- [x] Distinguish Execution Time, Data Interval and Duration
- [x] Understand Backfill
- [x] Understand Idempotency
- [x] Connect Retry to Idempotency
- [x] Design partition-scoped recovery
- [x] Reconnect Atomic Publish to pipeline reliability
- [x] Recognize concurrent-run risks



## Session 24 — Pipeline State & Observability

### Goal

Understand how pipeline execution state and evidence make failures
observable, diagnosable and recoverable.

### Definition vs Execution

A pipeline definition describes the workflow.

    orders_pipeline

Each execution creates a separate Pipeline Run.

    orders_pipeline
        ├── Run Sep 7
        ├── Run Sep 8
        └── Run Sep 9

The definition is reusable.
Each run has its own state and execution history.

### Task Instance

A task definition may execute many times.

    customer_stats
        ├── Sep 7 / attempt 1 → SUCCESS
        ├── Sep 8 / attempt 1 → FAILED
        ├── Sep 8 / attempt 2 → SUCCESS
        └── Sep 9 / attempt 1 → SUCCESS

Execution state therefore belongs to a Task Instance,
not only to the Task Definition.

### Task State

A simplified lifecycle:

    WAITING
       ↓
    READY
       ↓
    RUNNING
       ↓
    SUCCESS / FAILED

With retry:

    FAILED
       ↓
    RETRY_WAIT
       ↓
    READY
       ↓
    RUNNING

### State, Logs and Metrics

State:

    Where is the execution in its lifecycle? 
    
    OR 
    
    WHERE are we?

Logs:

    What happened during execution?

    OR

    WHAT happened?

Metrics:

    How is the system behaving quantitatively over time?

    OR

    HOW are we doing over time?

These provide complementary evidence.

### Success vs Health

A pipeline may remain successful while approaching an SLA violation.

Example:

    10 → 12 → 17 → 25 → 29 minutes

    SLA = 30 minutes

State:

    SUCCESS

Metric trend:

    Performance is deteriorating.

**Success does not necessarily mean healthy.**

### Execution History

Useful execution evidence includes:

    run_id
    pipeline_name
    task_name
    data_interval
    attempt
    started_at
    finished_at
    duration
    status
    error_message

A Run ID allows evidence from the same execution to be correlated.

### Observability

Observability provides enough external evidence to understand
the internal behavior of pipeline execution.

Conceptually:

                Pipeline
                   │
          ┌────────┼────────┐
          ▼        ▼        ▼
        State     Logs    Metrics
          └────────┼────────┘
                   ▼
             Observability

- **State  → WHERE are we?**
- **Log    → WHAT happened?**
- **Metric → HOW are we doing over time?**

### MTTR

Mean Time To Recovery represents how long it takes to restore normal
operation after a failure.

    Better Evidence
        ↓
    Faster Diagnosis
        ↓
    Targeted Recovery
        ↓
    Lower MTTR

### Key Insights

- Pipeline Definition and Pipeline Run are different concepts.
- Task Definition and Task Instance are different concepts.
- Execution state belongs to a specific execution instance.
- State, Logs and Metrics answer different operational questions.
- SUCCESS does not necessarily mean HEALTHY.
- Execution evidence should support correlation.
- Observability enables faster diagnosis and targeted recovery.

### Principle

**If a system can fail, it should leave enough evidence to explain the failure.**

### Definition of Done

- [x] Distinguish Pipeline Definition and Pipeline Run
- [x] Understand Task Instance
- [x] Understand execution State
- [x] Distinguish State, Logs and Metrics
- [x] Recognize degrading health before failure
- [x] Understand execution history
- [x] Understand evidence correlation
- [x] Connect Observability to MTTR


## Session 25 — Sprint Review

### Goal

Decide when workflow orchestration is justified and consolidate
the architectural model developed throughout Sprint 5.

### Orchestration Decision

An orchestrator is not justified merely because a system contains data pipelines.

Consider:

    Coordination Complexity
    Scheduling Requirements
    Dependency Complexity
    SLA
    Failure Recovery
    Retry / Backfill
    Parallel Execution
    Observability
    Operational Cost

Simple pipelines may remain manually operated when coordination cost is low.

### Decision Principle

    Requirements
        ↓
    Coordination Complexity
        ↓
    Quality Attributes
        ↓
    Existing Solution
        ↓
    Does it satisfy requirements?
        │
       YES
        ↓
    Is there a measurable problem worth solving?
        │
      NO → Keep it simple
      YES
        ↓
    Compare benefit vs migration cost

**Standardization is a trade-off, not an automatic justification.**

### Performance and Observability

A successful pipeline may still be approaching SLA failure.

Example:

    Duration:
    40 → 48 → 53 → 57 min

    SLA:
    60 min

Metrics detect the degradation trend.

Task-level metrics narrow the investigation.

Logs then help explain the underlying cause.

### Orchestrator

An orchestrator coordinates when tasks run, what they depend on, and how their execution is managed.

It coordinates work rather than performing all processing itself.

### Sprint Mental Model

    BUSINESS PIPELINE
       ↓
    DAG DEFINITION
    Tasks + Dependencies
        ↓
    SCHEDULING
    When + Data Interval
        ↓
    EXECUTION
    Run + Task Instances
        ↓
    STATE & OBSERVABILITY
    State + Logs + Metrics + History
        ↓
    FAILURE?
    ┌───┴────┐
    NO       YES
    │         ↓
    │      RETRY
    │         ↓
    │    IDEMPOTENT
    │    RE-EXECUTION
    │         ↓
    │     VALIDATE
    │         ↓
    │   ATOMIC PUBLISH
    │         │
    └────┬────┘
         ↓
    RELIABLE DATA PIPELINE

### Sprint Principle

**Define dependencies → schedule work → track execution → observe evidence → recover safely → publish valid data.**

### Definition of Done

- [x] Understand why orchestration exists
- [x] Model workflows as DAGs
- [x] Understand upstream/downstream dependencies
- [x] Understand Fan-out and Fan-in
- [x] Understand Critical Path
- [x] Understand scheduling and data intervals
- [x] Understand Retry and Backfill
- [x] Connect Retry to Idempotency
- [x] Understand Pipeline Runs and Task Instances
- [x] Distinguish State, Logs and Metrics
- [x] Connect Observability to MTTR
- [x] Decide when orchestration is justified
- [x] Avoid technology-first architecture

## Sprint Status

### We have built so far:

    Data Lake
    +
    Parquet
    +
    Physical Layout
    +
    Spark
    +
    Distributed Processing
    +
    Reliable Pipeline Concepts
    +
    Orchestration Model

**COMPLETED**


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