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