# Big Data Architecture Playground --- Evidence-Based Learning Course

**30 Sessions + Final Course Review**\
**Status:** Reconstructed canonical learning guide

## About this course

This document reconstructs the **30-session Big Data Playground learning
path** as a reusable course.

It is intentionally **not a conversation transcript**. Learner answers,
back-and-forth discussion, debugging chatter, and personal exchanges
have been removed. What remains is the teaching path:

**Problem → Prediction → Experiment → Evidence → Mental Model →
Trade-off → Architecture Principle**

### Accuracy note

The course sequence, experiments, important measurements, architectural
decisions, and core questions are reconstructed from the available
Playground records and course history. Where the original wording of an
old question was not preserved, the question is editorially
reconstructed to preserve the same learning objective rather than
presented as a verbatim quotation.

### How to use this course

For each session, read the problem and mental model, answer the
questions **before** running the experiment, run the smallest experiment
that can produce useful evidence, compare prediction with observation,
and record the principle rather than merely the command.

> **Course rule:** No technology without a problem, no decision without
> a trade-off, and no claim without evidence.

------------------------------------------------------------------------

# Part I --- Container & Data Foundations

## Session 01 --- Containers: Why Docker?

### Goal

Understand why a reproducible execution environment is useful before
learning Docker commands.

### Problem

A program can work on one machine and fail on another because the
application depends on runtime versions, libraries, configuration, and
operating-system assumptions. Docker gives us a repeatable execution
boundary.

### Mental model

**Image** = immutable recipe/template for an environment.\
**Container** = running instance of an image.\
Analogy: **Class → Object; Image → Container**.

### Experiment

Run a minimal container such as `hello-world`. Inspect local images and
containers.

### Questions to answer

1.  What is the difference between an image and a container?
2.  If a container is deleted, is its image necessarily deleted?
3.  Why is a container more reproducible than installing everything
    manually?
4.  What problem is Docker solving here: application logic or execution
    environment?

### Key principle

> **Package the execution environment so that "where it runs" changes
> less of "how it behaves."**

------------------------------------------------------------------------

## Session 02 --- Dockerfile, Build Context & Layers

### Goal

Understand how an image is constructed and why Docker builds are
layered.

### Problem

We need a repeatable way to describe how an application environment is
built.

### Mental model

**Source → Build Context → Dockerfile → Image Layers → Image**

### Experiment

Create a small Dockerfile, build it, modify only a later instruction,
and build again. Observe cache reuse.

### Questions to answer

1.  Why can the second build be faster than the first?
2.  What happens to cache reuse if a frequently changing file is copied
    too early?
3.  Why should the build context be intentionally small?
4.  What is the difference between source code and a deployable image?

### Key principle

> **Build structure affects repeatability and build cost.**

------------------------------------------------------------------------

## Session 03 --- `.dockerignore` & Build Boundaries

### Goal

Understand why excluding irrelevant files is part of defining a clean
build boundary.

### Problem

A repository may contain logs, generated output, Git metadata, local
files, and secrets that do not belong in an image build.

### Experiment

Compare the build context before and after introducing `.dockerignore`.

### Questions to answer

1.  Why is sending the whole repository to the Docker build context
    unnecessary?
2.  What risks arise if local secrets or generated files enter the build
    context?
3.  Is `.dockerignore` merely a performance optimization?
4.  What should determine whether a file belongs inside the build
    boundary?

### Key principle

> **A clean build boundary contains only what is required to produce the
> deployable artifact.**

------------------------------------------------------------------------

## Session 04 --- Container Networking

### Goal

Understand communication between containers and why `localhost` is
contextual.

### Problem

An application container needs to communicate with another service such
as PostgreSQL. Inside a container, `localhost` refers to that container
itself.

### Mental model

-   Container → container: use the service name.
-   Container → host: use the appropriate host bridge mechanism such as
    `host.docker.internal` where supported.
-   Host → container: usually use a published host port.

### Questions to answer

1.  If Python and PostgreSQL run in different containers, why should
    Python not connect to `localhost:5432`?
2.  What does a Compose service name represent from another container?
3.  Why are network names part of the runtime contract?
4.  What changes when the database moves from host to container?

### Key principle

> **`localhost` means "this network namespace," not "the machine I am
> thinking about."**

------------------------------------------------------------------------

## Session 05 --- Docker Compose: A Small System, Not One Container

### Goal

Move from individual containers to a multi-service system.

### Problem

Starting services manually leaves operational knowledge in the
developer's memory.

### Mental model

**Services + Networks + Volumes + Configuration**

### Experiment

Define PostgreSQL and an application/utility service in Compose. Bring
the environment up and down as one unit.

### Questions to answer

1.  What knowledge moves from manual commands into `compose.yaml`?
2.  Does Compose make two services one application process?
3.  Why is service separation useful even on one laptop?
4.  What should survive `docker compose down`?

### Key principle

> **Describe the runtime topology as configuration instead of relying on
> human memory.**

------------------------------------------------------------------------

## Session 06 --- Persistence with PostgreSQL Volumes

### Goal

Understand why container lifecycle and data lifecycle must be separated.

### Problem

Containers are replaceable. Database state usually is not.

### Experiment

Run PostgreSQL with a named volume, insert data, stop/remove containers,
and recreate them. In the PostgreSQL 18 Playground image, persistence
used `/var/lib/postgresql`.

### Questions to answer

1.  Why should persistent database state not depend on a particular
    container instance?
2.  What survives `docker compose down`?
3.  What additional effect does `docker compose down -v` have?
4.  Which lifecycle is longer: container or durable data?

### Key principle

> **Compute can be replaceable while state has an independent
> lifecycle.**

------------------------------------------------------------------------

## Session 07 --- Port Mapping & System Boundaries

### Goal

Understand the distinction between a container port and a host-published
port.

### Mental model

`HOST_PORT:CONTAINER_PORT`

### Questions to answer

1.  If PostgreSQL listens on 5432 inside its container, do other Compose
    services need the host-published port?
2.  Why can environments use different host ports while keeping the same
    container port?
3.  Which boundary does port mapping cross?
4.  Should every internal service port be published to the host?

### Key principle

> **Expose only the boundaries that actually need to be crossed.**

------------------------------------------------------------------------

## Session 08 --- First Data Pipeline

### Goal

Build the first end-to-end data flow: CSV → ingestion container →
PostgreSQL.

### Pipeline

**`orders.csv` → Python ingestion → PostgreSQL**

### Experiment

Mount `../datasets:/data:ro`, verify that writes fail, then ingest five
orders using row-by-row `INSERT` with
`ON CONFLICT (order_id) DO NOTHING`. Run twice.

### Evidence

First run inserts five rows. Second run still leaves five rows.

### Questions to answer

1.  Why mount source data read-only?
2.  What should happen if the same ingestion job runs twice?
3.  Why is safe rerun important for future automation?
4.  What is the difference between bringing the whole system up and
    running one ingestion job?

### Concepts

**Idempotency**, **one-off job**.

### Key principle

> **A data pipeline should be safe to execute again whenever
> practical.**

------------------------------------------------------------------------

## Session 09 --- Reliability: Started ≠ Ready

### Goal

Understand dependency readiness and transient failure recovery.

### Experiment A --- Readiness

Add a PostgreSQL health check using `pg_isready` and make ingestion
depend on database health.

### Experiment B --- Transient failure

Temporarily use an invalid database host and add bounded exponential
retry: **1s → 2s → 4s → 8s**, finite attempts.

### Questions to answer

1.  Is "container started" equivalent to "database ready"?
2.  Which failures should be retried?
3.  Should invalid credentials or invalid data be retried forever?
4.  Why must retry be bounded?
5.  What is the difference between transient and permanent failure?

### Key principle

> **Readiness is a dependency guarantee; retry is appropriate only when
> time may repair the failure.**

------------------------------------------------------------------------

## Session 10 --- Architecture Review & Ingestion Performance

### Goal

Introduce Quality Attributes and measure before optimizing.

### Quality Attributes

Performance, Reliability, Data Quality, Observability, Security.

### Experiment --- 100,000 rows

Row-by-row INSERT: **8.08 s**, **12,369 rows/s**.\
PostgreSQL COPY: **0.10 s**, **988,933 rows/s**, about **80×** measured
throughput.

Introduce invalid `amount=ABC` around row 53,217 after truncating the
destination. COPY fails and final row count remains **0**.

### Questions to answer

1.  Why benchmark before deciding row-by-row INSERT is too slow?
2.  What Quality Attribute does COPY primarily improve?
3.  What do we gain and lose with bulk loading?
4.  If one bad row causes the entire COPY to fail, is that always bad?
5.  What architectural need does coarse failure granularity suggest?

### Concepts

Quality Attribute, Baseline, Throughput, Bulk Load, Failure Granularity,
Atomicity, Staging Area.

### Key principle

> **Performance improvements change failure behavior too; measure
> both.**

------------------------------------------------------------------------

# Part II --- Analytical Storage & Data Lake

## Session 11 --- CSV vs Parquet

### Goal

Understand why analytical storage format affects how much data must be
processed.

### Experiment

Convert 100,000 orders from CSV to Parquet.

-   CSV: **2.54 MB**
-   Parquet: **0.62 MB**
-   Conversion: **0.10 s**
-   About **76% smaller** in this dataset.

Write four row groups of 25,000 rows. Query `amount` where
`order_id > 80000`.

Small-query comparison: - Parquet: **0.430843 s** - pandas CSV:
**0.067223 s**

CSV is faster in this tiny experiment.

### Questions to answer

1.  If Parquet is designed for analytics, why can CSV be faster here?
2.  Which columns must be read for
    `WHERE order_id > 80000 SELECT amount`?
3.  What allows row groups to be skipped?
4.  At what scale does avoided work repay Parquet's fixed overhead?
5.  Why is "Parquet is faster" an unsafe universal claim?

### Concepts

Columnar Storage, Row Group, Column Pruning, Data Skipping, Crossover
Point.

### Key principle

> **Do not process data you do not need.**

------------------------------------------------------------------------

## Session 12 --- Partitioning

### Goal

Choose physical partitioning from workload rather than technology
fashion.

### Workload

Daily revenue, monthly revenue, month comparison, occasional whole-year
query; customer-specific queries uncommon.

### Experiment --- 1,000,000 orders in 2026

Layouts: - Non-partitioned: 1 file - By month: 12 partitions - By day:
365 partitions

Write times: **0.236 s / 0.591 s / 4.726 s**.

Daily query: **0.030599 s / 0.008411 s / 0.004164 s**.\
August query: **0.043685 s / 0.007643 s / 0.054943 s**.\
Year query: **0.026792 s / 0.024896 s / 0.571435 s**.

### Correctness discovery

A physical partition key is a correctness contract. If a row for Aug 28
is stored under Aug 27, pruning Aug 28 may skip valid data.

### Questions to answer

1.  Which layout is fastest for a daily query?
2.  Which layout is best for the stated overall workload?
3.  Why can 365 partitions hurt a yearly query?
4.  Is the fastest design for one query automatically the best
    architecture?
5.  What if future workload becomes 90% daily?
6.  Why is partition correctness as important as partition performance?

### Decision

Choose **monthly partitioning** for the stated workload.

### Key principle

> **Partitioning does not make a query fast; pruning does. Design
> physical layout from access patterns.**

------------------------------------------------------------------------

## Session 13 --- Query Optimization & Predicate Pushdown

### Goal

Separate predicate pushdown, metadata, and actual data skipping.

### Mental model

**Partition Pruning → Data Skipping → Column Pruning → Predicate
Filtering**

### Experiment A --- Unsorted 1M rows, 10 row groups

For `order_id > 900000`, metadata can reject nine groups. For random
`amount > 900`, all groups contain qualifying ranges.

Measured: - ORDER_ID after-read **0.062166 s**, pushdown **0.006015
s** - AMOUNT after-read **0.028452 s**, pushdown **0.027473 s**

### Experiment B --- Sort by amount

Measured: - ORDER_ID after-read **0.068777 s**, pushdown **0.021306
s** - AMOUNT after-read **0.028382 s**, pushdown **0.006205 s**

Sorting improves one access pattern and weakens another.

### Questions to answer

1.  Does predicate pushdown guarantee row-group skipping?
2.  Why does `order_id > 900000` benefit strongly before sorting by
    amount?
3.  Why does `amount > 900` initially skip almost nothing?
4.  What do you predict after sorting physically by `amount`?
5.  Why can optimizing one predicate weaken another?
6.  Can equal result cardinality still have very different query cost?

### Key principle

> **A good physical layout is workload-aware. The engine can optimize
> only what it understands.**

------------------------------------------------------------------------

## Session 14 --- Data Lake Foundations

### Goal

Separate source truth, validated data, and business-ready data.

### Zones

**Raw** --- preserve source truth.\
**Cleaned** --- validate and normalize.\
**Curated** --- business-ready outputs.

### Experiment

Build cleaned Parquet with checks for required columns, nulls, numeric
values, dates, duplicate IDs, and negative amounts. Produce
daily/monthly revenue. Introduce `ABC` and observe failure.

A stale-output risk appears, motivating future **write temp → validate →
publish**.

### Questions to answer

1.  Why preserve Raw if Cleaned already exists?
2.  Why should experiment files not automatically become business data?
3.  What is a Data Contract?
4.  If a run fails but old output remains, how does a consumer know
    freshness?
5.  What should happen before new output becomes visible?

### Key principle

> **Preserve source truth, validate before trust, publish only valid
> data.**

------------------------------------------------------------------------

## Session 15 --- Sprint Review: When Is One Machine No Longer Enough?

### Goal

Create the decision boundary that gives distributed processing a reason
to exist.

### Decision model

**Reduce unnecessary work → Measure against SLA → Optimize / Scale Up →
Still insufficient? → Scale Out**

### Questions to answer

1.  A job takes 20 minutes with a 30-minute SLA. Do we need Spark?
2.  A job takes three hours with a 30-minute SLA after reasonable
    optimization. What changes?
3.  Which comes first: more machines or less unnecessary work?
4.  What evidence justifies distributed-processing operational cost?
5.  Is "5 billion rows" by itself an architecture requirement?

### Key principle

> **Before adding compute, reduce unnecessary work. Dataset size alone
> does not justify distributed processing.**

------------------------------------------------------------------------

# Part III --- Distributed Processing

## Session 16 --- Why Distributed Processing? Partition → Task → Worker

### Goal

Understand scale-out without starting from Spark terminology.

### Problem

A 1 TB optimized workload takes three hours on one machine; SLA is 30
minutes.

### Mental model

**Split → Process independently → Combine**

**Storage partition** decides what can be skipped.\
**Processing partition** decides what can run in parallel.

### Questions to answer

1.  Why might four workers finish sooner than one?
2.  Will four workers always make the job four times faster?
3.  What happens when one partition is much larger?
4.  Why can too many tiny tasks hurt?
5.  What is the difference between storage and processing partitions?

### Key principle

> **Partitioning creates parallelism boundaries --- and later, recovery
> boundaries.**

------------------------------------------------------------------------

## Session 17 --- Spark Fundamentals

### Goal

Map generic distributed-processing concepts onto Spark.

### Mental model

**Application → Job → Stage → Task**\
**Driver** coordinates; **Executors** compute.\
Transformations describe work; Actions trigger execution.

### Experiment

Run `local[4]` against 1M cleaned rows. Observe four processing
partitions and inspect a filter plan for pushed filters and reduced read
schema.

### Questions to answer

1.  Are ten Parquet row groups necessarily ten Spark processing
    partitions?
2.  What does the Driver do?
3.  What does an Executor do?
4.  Why can Spark delay execution after transformations?
5.  Does `PushedFilters` prove row groups were actually skipped?

### Key principle

> **A distributed engine plans work before executing it; storage and
> processing partitions are related but not identical.**

------------------------------------------------------------------------

## Session 18 --- Distributed Aggregation & Shuffle

### Goal

Understand why data movement is often expensive.

### Problem

Records for the same product can live in different partitions and must
logically meet for global aggregation.

### Mental model

> **Shuffle happens when related data must meet.**

### Experiment

Inspect a `groupBy(product)` plan. Observe partial aggregation,
`Exchange hashpartitioning(...)`, final aggregation, and AQE behavior.

### Questions to answer

1.  Why can each partition not independently produce the final global
    total?
2.  What must move across partitions?
3.  Why does shuffle create a Stage boundary?
4.  Why is partial aggregation before shuffle useful?
5.  Why should we avoid claiming an exact final partition count without
    runtime evidence?

### Key principle

> **Reduce data before moving data whenever possible: process less, move
> less, coordinate less.**

------------------------------------------------------------------------

## Session 19 --- Failure, Retry & Lineage

### Goal

Understand recovery at smaller units of work.

### Experiment

Run four partitions with a controlled first-attempt failure in
partition 1. Final evidence shows partition 1 on attempt 1 while the
others remain on attempt 0.

### Questions to answer

1.  Should one failed task force every successful task to run again?
2.  What allows Spark to recompute work?
3.  What is the difference between Narrow and Wide Dependency?
4.  Which failures are sensible retry candidates?
5.  What does this experiment prove --- and not prove --- about
    worker-machine failure?

### Key principle

> **Recovery should happen at the smallest practical unit of failure.**

------------------------------------------------------------------------

## Session 20 --- Distributed Processing Architecture Review

### Goal

Turn Spark knowledge into a technology decision model.

### Review model

**Business Workload → Quality Attributes → Data Layout → Process Less →
Measure → Optimize / Scale Up → Scale Out only if necessary**

### Questions to answer

1.  Does a large dataset automatically justify Spark?
2.  What bottleneck would Spark actually solve?
3.  When does Amdahl's Law limit parallel speedup?
4.  Why can a straggler determine completion time?
5.  If one machine already satisfies SLA, what value does Spark add
    relative to cost?

### Key principle

> **Do not ask "Is this Big Data?" Ask "Which identified bottleneck
> would distributed processing solve?"**

------------------------------------------------------------------------

# Part IV --- Workflow Orchestration

## Session 21 --- Why Orchestration?

### Goal

Discover orchestration from coordination pain rather than an Airflow
tutorial.

### Problem

Humans know which Raw → Cleaned → Curated job runs first, when to start
the next, what to retry, and what failed.

### Mental model

**Dependency + State + Scheduling + Retry**

Processor: **How is data processed?**\
Orchestrator: **Which job should run, when, and after what?**

### Questions to answer

1.  What knowledge currently exists only in the operator's head?
2.  Which jobs must wait and which may run concurrently?
3.  Does an orchestrator perform business transformation itself?
4.  When is adding an orchestrator unnecessary?

### Key principle

> **Do not introduce an orchestrator because pipelines exist; introduce
> it when coordinating pipelines becomes a real problem.**

------------------------------------------------------------------------

## Session 22 --- DAG Fundamentals & Critical Path

### Concepts

DAG, Task, Dependency, Upstream/Downstream, Fan-out/Fan-in, Topological
Order, Critical Path.

Course example critical path: **A → B → D → F = 60 minutes**.

### Questions to answer

1.  Why must an orchestration DAG be acyclic?
2.  What is the difference between topological order and a path?
3.  Which tasks can run simultaneously after fan-out?
4.  Which path determines earliest workflow completion?
5.  If you can optimize one task, should you automatically choose the
    longest individual task?

### Key principle

> **Optimize the work that actually constrains completion.**

------------------------------------------------------------------------

## Session 23 --- Scheduling, Idempotency & Backfill

### Goal

Understand time as part of the execution contract.

### Concepts

Execution Time, Data Interval, Duration, Backfill, Idempotency, Race
Condition, Concurrency Control, Atomic Publish.

### Recovery model

**Failure → Retry → Idempotent Re-execution → Validate → Atomic Publish
→ Reliable Output**

### Questions to answer

1.  If a daily job runs today, must it process today's data?
2.  Why should business scope be explicit rather than inferred from
    wall-clock time?
3.  Why does retry require safe re-execution?
4.  What can happen if two runs publish the same partition concurrently?
5.  How should a historical date be republished safely?

### Key principle

> **Retry capability is an orchestrator feature; safe retry is a system
> property.**

------------------------------------------------------------------------

## Session 24 --- State & Observability

### Goal

Understand what evidence answers "What happened?"

### Concepts

Pipeline Definition vs Pipeline Run; Task Definition vs Task Instance;
State, Logs, Metrics, Execution History, Correlation ID, MTTR.

Typical lifecycle: **WAITING → READY → RUNNING → SUCCESS / FAILED**.

### Questions to answer

1.  What is the difference between a task definition and task instance?
2.  Is SUCCESS sufficient to say a pipeline is healthy?
3.  If duration rises from 10 to 25 minutes against a 30-minute SLA,
    what evidence already exists?
4.  What additional evidence would localize the bottleneck?
5.  Why is a correlation/run ID useful?

### Key principle

> **Measure at every meaningful execution boundary so cost and failure
> can be localized progressively.**

------------------------------------------------------------------------

## Session 25 --- Orchestration Architecture Review

### Goal

Decide when orchestration is justified and connect observability to
root-cause reasoning.

### Root-cause model

**Observed Evidence → Observed Problem → Potential Impact → More
Evidence → Root Cause**

### Questions to answer

1.  Should a tiny, rarely executed pipeline automatically receive an
    orchestrator?
2.  Is standardization alone enough reason to migrate another system?
3.  What is the smallest practical failure/recovery boundary?
4.  If metrics already show increasing duration, should the next step
    merely be "check metrics"?
5.  Does an orchestrator coordinate processing or replace all processing
    logic?

### Key principle

> **Localize first, diagnose second. Root cause is evidence-supported,
> not merely the nearest visible symptom.**

------------------------------------------------------------------------

# Part V --- Technology Evaluation & Airflow Walking Skeleton

## Session 26 --- Requirements → Evaluate Orchestration Technologies

### Goal

Choose technology from requirements instead of popularity.

### Requirements

Dependency management, Scheduling, State, Retry, Backfill,
Observability, Local/Docker friendliness.

### Candidates

Apache Airflow, Prefect, Dagster.

### Framework

**Problem → Requirements → Hard Constraints → Candidate Filtering →
Criteria → Trade-offs → Technology Hypothesis → PoC → Evidence →
Decision**

### Questions to answer

1.  Which requirements are hard constraints and which are weighted
    criteria?
2.  Would you build a custom orchestrator just to learn orchestration?
3.  If X has 30 features and Y has only what we need with lower
    complexity, which is preferable?
4.  How should ecosystem maturity affect a long-lived choice?
5.  Which candidate should become the Playground hypothesis, and why?

### Technology hypothesis

Use **Apache Airflow** provisionally. Do **not** create the final ADR
yet.

### Key principle

> **Select a technology hypothesis, then validate it with evidence.**

------------------------------------------------------------------------

## Session 27 --- First Real DAG

### Goal

Prove dependency before adding scheduling, retry, or backfill.

### DAG

**build_cleaned_orders → build_revenue_curated**

### Prediction experiment

Add 10-second delays to both tasks and remove the dependency.

### Questions to answer

1.  If cleaned takes ten minutes, may curated start after two minutes
    when dependency exists?
2.  If dependency is removed but one task appears first in Python
    source, must execution remain sequential?
3.  Which timestamps would prove parallelism?
4.  What value is created when dependency knowledge moves out of human
    procedure?

### Evidence

Without dependency both delayed tasks start together.

> **Code order ≠ execution order.**

### Real processing integration

Airflow invokes existing processing scripts.
`subprocess.run(..., check=True)` propagates non-zero process exit into
task failure.

### Control Plane vs Data Plane

**Airflow / Control Plane** --- WHEN, ORDER, STATE, RETRY.\
**Processing / Data Plane** --- READ, VALIDATE, TRANSFORM, AGGREGATE,
WRITE.

### Key principle

> **Move execution knowledge from humans into machine-readable
> dependencies. Logical boundaries do not always require physical
> boundaries.**

------------------------------------------------------------------------

## Session 28 --- Scheduling + Retry + Backfill

### Goal

Prove three orchestration capabilities while separating tool capability
from business correctness.

### Experiment A --- Scheduling

Use a temporary five-minute schedule and observe an automatic scheduled
run.

### Experiment B --- Retry

Create a task that fails first and later succeeds. `retries=2` means one
initial attempt plus up to two retries.

### Experiment C --- Backfill

Create a daily experiment DAG and request Sep 8--10, 2026 historical
runs. Observe three independent backfill DAG Runs.

Actual Airflow 3.3.1 runtime evidence showed the backfill context's
interval start/end equal to each logical timestamp; evidence overrode
the earlier expectation.

### Questions to answer

1.  Which responsibility creates runs automatically?
2.  What is the difference between Execution Time and Data Interval?
3.  Does Airflow backfill automatically make processing historically
    correct?
4.  Why should three historical dates have independent execution state?
5.  How should orchestration communicate business scope to processing?

### Important gap

**Airflow can backfill ≠ the business pipeline is backfill-correct.**

Candidate future contract: **DAG Run date → explicit business date →
process only that date → publish only that date**.

### Key principle

> **Scheduling, Retry, and Backfill are orchestration capabilities;
> correctness still depends on the execution contract with processing.**

------------------------------------------------------------------------

## Session 29 --- Failure, State & Observability

### Goal

Use execution evidence to localize a permanent failure before diagnosing
it.

### Experiment

**extract_data → transform_data → publish_data**. `extract_data` raises
`FileNotFoundError: /lake/raw/ilostat/input.csv does not exist`, with
`retries=2`.

### Prediction questions

1.  How many total attempts can `extract_data` make?
2.  What should its final state be if the file never appears?
3.  Should transform and publish execute?
4.  Where should troubleshooting begin: all logs or the nearest failed
    boundary?

### Evidence

-   DAG Run: **FAILED**
-   `extract_data`: **FAILED**, Try **3**
-   `transform_data`: **UPSTREAM FAILED**, Try **0**
-   `publish_data`: **UPSTREAM FAILED**, Try **0**

### Troubleshooting model

**State → Failure Location → Attempts → Logs → Verify Evidence → Root
Cause**

### Questions to answer

1.  Is every failure retryable?
2.  Can retry repair a permanently missing file?
3.  What does repeated identical failure across attempts suggest?
4.  Can DAG → Task → Attempt → Log locate the cause without reading
    every pipeline log?

### Key principles

> **Retry is a recovery mechanism, not a repair mechanism.**\
> **Observability reduces the search space between symptom and cause.**

------------------------------------------------------------------------

## Session 30 --- Architecture Review: Manual Pipeline → Production-like Data Pipeline

### Goal

Decide whether Airflow should be accepted based on evidence from
Sessions 27--29.

### Requirements vs evidence

  Requirement     Playground evidence
  --------------- ----------------------------------------
  Dependency      Real cleaned → curated order
  Scheduling      Automatic scheduled DAG Run
  State           SUCCESS / FAILED / UPSTREAM FAILED
  Retry           Controlled transient failure recovered
  Backfill        Independent historical DAG Runs
  Observability   DAG → Task → Attempt → Log
  Local/Docker    Airflow ran locally in Docker

### Architecture questions

1.  Based on Sessions 27--29, should Airflow be accepted for the
    Playground? Why?
2.  What is the main trade-off introduced by Airflow?
3.  If ILOSTAT MVP has one source, one country, and a few weekly jobs,
    should Airflow be used automatically?

### Decision

Accept Airflow for the **Big Data Playground**. For ILOSTAT, Airflow is
only an **initial candidate** and must be reevaluated against real
coordination complexity and Quality Attributes.

### Scalability distinction

**Spark → scale computation**\
**Airflow → scale coordination**

### Key principle

> **Technology decisions are contextual, not transferable by default.**

------------------------------------------------------------------------

# Final Course Review --- Architecture & Production Gap Map

## What the course actually taught

The course did not teach a mandatory Big Data stack. It built a
reasoning chain:

**Business Problem → Quality Attributes → Data Architecture → Storage →
Processing → Distributed Processing when justified → Orchestration when
justified → Data Product**

Technologies were instruments used to produce evidence.

## Storage mental model

**CSV → Parquet → Row Groups → Column Pruning → Predicate Pushdown →
Data Skipping → Partition Pruning**

> **Do not process data you do not need.**

## Data Lake mental model

**Raw → Cleaned → Curated → Data Product**

-   Raw preserves source truth.
-   Cleaned validates and normalizes.
-   Curated adds business meaning.
-   A Data Product serves a useful consumer need.

> **Preserve source truth, validate before trust, publish only valid
> data.**

## Distributed-processing mental model

**Workload → Reduce unnecessary work → Measure → SLA met?**

If yes, keep the simpler architecture. If no: **Optimize → Scale Up →
Measure → Still insufficient? → Evaluate Scale Out**.

Core model: **Partition → Task → Worker/Executor → Parallelism**.

## Orchestration mental model

Orchestration becomes useful when coordination becomes a problem.

Core responsibilities: Dependency, Scheduling, State, Retry, Backfill,
Execution History, Observability.

## Architecture decision mental model

**Problem → Requirements → Quality Attributes → Options → Trade-offs →
Experiment → Evidence → Decision**

A technology is initially a **hypothesis**, not a conclusion.

### Architect's questions

1.  What problem are we solving?
2.  What evidence shows the problem exists?
3.  Which Quality Attribute is affected?
4.  What happens if we do nothing?
5.  What options could solve it?
6.  What benefit does each option provide?
7.  What trade-off does each option introduce?
8.  Is there a simpler option?
9.  What experiment could validate the decision?

## Final Big Data challenge

Someone says: "This is a Big Data project. Let's build Spark + Airflow +
Data Lake from the beginning so we won't need to change later."

Ask: 1. Why do we call this Big Data? 2. Even if it is Big Data, why
does that imply Spark, Airflow, or a Data Lake? 3. Which specific
problem does each technology solve? 4. What benefit does each provide
compared with not using it? 5. What cost and trade-off does each
introduce? 6. Are there simpler or better options under current
requirements? 7. What evidence would prove the choice is justified?

This is the final shift from technology-driven thinking to
architecture-driven thinking.

------------------------------------------------------------------------

# Production Gap Map

The Playground is an **architectural walking skeleton**, not a
production platform.

  -----------------------------------------------------------------------
  Area                    Playground              Deferred production
                                                  concern
  ----------------------- ----------------------- -----------------------
  Storage                 Local filesystem        Object/distributed
                                                  storage

  File format             Parquet                 Schema evolution and
                                                  compatibility

  Data Lake               Raw/Cleaned/Curated     Catalog, ownership,
                                                  governance, lineage

  Publishing              Basic file output       Atomic/transactional
                                                  publishing

  Processing              Python + local Spark    Cluster deployment,
                                                  sizing, tuning

  Orchestration           Airflow standalone      Production deployment,
                                                  HA, upgrades

  Security                Minimal                 Secrets, AuthN, AuthZ,
                                                  encryption

  Observability           State, attempts, logs   Metrics, alerts,
                                                  tracing, SLOs

  Reliability             Retry/backfill          DR, HA, recovery
                                                  objectives

  Data Quality            Basic validation        Continuous
                                                  quality/freshness
                                                  monitoring

  Operations              Local Docker            Production CI/CD and
                                                  environment management
  -----------------------------------------------------------------------

These are **deferred complexity**, not forgotten architecture.

### Deferred-learning rule

**Known Gap → Real Requirement?** - **No** → keep deferred. - **Yes** →
define problem → identify Quality Attribute → evaluate options → compare
trade-offs → experiment → gather evidence → decide.

------------------------------------------------------------------------

# Transition to ILOSTAT Career Data Platform

The Playground was **learning-driven**:

**Concept → Experiment → Evidence → Mental Model**

ILOSTAT should be **problem-driven**:

**Real Problem → Requirements → Quality Attributes → Smallest Useful
Architecture Decision → Implementation → Measurement → Evidence → Next
Problem**

Begin with the smallest useful vertical slice:

**One real ILOSTAT source → Raw → Cleaned → Vietnam → One occupation
dimension → One useful indicator → One query/API → One visualization →
One useful career insight**

The first goal is not "Build a Big Data Platform."

> **Use real labour-market data to produce one useful insight for a real
> stakeholder.**

------------------------------------------------------------------------

# Core Architectural Vocabulary Map

## Data Storage & Query Optimization

-   **Columnar Storage** --- store values by column so analytical
    queries can avoid unrelated columns.
-   **Row Group** --- independently described Parquet block that can
    support skipping.
-   **Partition Pruning** --- avoid files/partitions that cannot satisfy
    the query.
-   **Data Skipping** --- avoid blocks whose metadata proves they cannot
    match.
-   **Column Pruning** --- read only columns required by the query.
-   **Predicate Pushdown** --- move filtering closer to the storage
    reader.

## Data Lake

-   **Raw** --- preserved source truth.
-   **Cleaned** --- validated and normalized data.
-   **Curated** --- business-ready analytical data.
-   **Data Contract** --- explicit expectations that data must satisfy.
-   **Data Product** --- data prepared for a useful consumer need.
-   **Reprocessability** --- rebuild derived data from retained source
    truth.
-   **Atomic Publish** --- expose new output only after it is valid.

## Distributed Processing

-   **Processing Partition** --- unit of data/work processed
    independently.
-   **Task** --- computation for a processing partition within a stage.
-   **Worker / Executor** --- process that executes tasks.
-   **Parallelism** --- simultaneous independent work.
-   **Data Skew** --- uneven distribution of work/data.
-   **Straggler** --- slow task that delays completion.
-   **Shuffle** --- move data so related records can meet.
-   **Lineage** --- transformation history used to recompute lost work.
-   **Recovery Granularity** --- smallest practical unit redone after
    failure.

## Scaling

-   **Scale Up** --- add resources to one machine.
-   **Scale Out** --- add machines/workers.
-   **SLA** --- required service/performance target.
-   **Amdahl's Law** --- serial work limits parallel speedup.

## Workflow Orchestration

-   **DAG** --- acyclic graph of tasks and dependencies.
-   **Critical Path** --- dependency path determining earliest
    completion.
-   **Scheduling** --- decide when workflow runs.
-   **Backfill** --- execute historical logical intervals.
-   **Task State** --- execution lifecycle such as
    READY/RUNNING/SUCCESS/FAILED.
-   **Failure Propagation** --- upstream failure affects downstream
    execution.
-   **Failure Localization** --- identify the smallest relevant failed
    boundary.
-   **Control Plane** --- coordinates execution and state.
-   **Data Plane** --- performs actual data processing.
-   **Execution Contract** --- agreement between orchestration and
    processing about scope and success/failure.

## Architecture Decision Making

-   **Quality Attribute** --- property such as performance, reliability,
    maintainability, or security.
-   **Baseline** --- measured starting point for comparison.
-   **Trade-off** --- improvement in one concern paid for elsewhere.
-   **Technology Hypothesis** --- testable belief that a technology can
    satisfy requirements.
-   **Decision Context** --- requirements and constraints within which a
    decision is valid.
-   **Deferred Complexity** --- known complexity postponed until a real
    requirement justifies it.

------------------------------------------------------------------------

# Course Principles --- One-page Review

1.  **Process less data before adding more compute.**
2.  **Partitioning does not make queries fast; pruning does.**
3.  **Design physical data layout from access patterns.**
4.  **The engine can optimize only what it understands.**
5.  **Preserve source truth, validate before trust, publish only valid
    data.**
6.  **Dataset size alone does not justify distributed processing.**
7.  **Shuffle happens when related data must meet.**
8.  **Recovery should happen at the smallest practical unit of
    failure.**
9.  **Move operational knowledge from human memory into machine-readable
    workflows.**
10. **Retry is a recovery mechanism, not a repair mechanism.**
11. **Tool capability does not automatically imply system capability.**
12. **Localize the failure before diagnosing the cause.**
13. **Observability reduces the search space between symptom and
    cause.**
14. **Technology decisions are contextual, not transferable by
    default.**
15. **No technology without a problem, no decision without a trade-off,
    and no claim without evidence.**

------------------------------------------------------------------------

# Course Completion

At the end of the 30 sessions, a learner should be able to reason about
a data platform without starting from a technology list.

The expected final behavior is to ask:

-   What problem exists?
-   What evidence do we have?
-   Which Quality Attribute matters?
-   What is the simplest viable option?
-   What does the option cost?
-   What experiment would change our mind?

That reasoning --- rather than memorizing Docker, Parquet, Spark, or
Airflow commands --- is the durable outcome of the Big Data Architecture
Playground.
