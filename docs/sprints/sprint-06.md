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