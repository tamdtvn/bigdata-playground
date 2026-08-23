# Sprint 2 — Data Engineering Foundation

## Session 6 — PostgreSQL & Persistent Storage

### Goal

Understand stateful services and how Docker volumes separate
data lifecycle from container lifecycle.

### Learned

- Containers are ephemeral.
- PostgreSQL is a stateful service because it owns persistent data.
- Without a volume, database data is tied to the container lifecycle.
- Docker volumes provide persistent storage independent of containers.
- `docker compose down` removes containers and networks but keeps
  named volumes by default.
- `docker compose down -v` also removes Compose-managed volumes.
- A volume is mounted into a container at a filesystem path.
- PostgreSQL 18 uses a new data directory layout and should mount
  `/var/lib/postgresql` rather than `/var/lib/postgresql/data`.

### Experiments

1. Started PostgreSQL without a volume.
2. Created a `playground` database.
3. Ran `docker compose down`.
4. Recreated the PostgreSQL container.
5. Verified that the `playground` database was lost.
6. Added a named Docker volume.
7. Mounted the volume at `/var/lib/postgresql`.
8. Created the `playground` database again.
9. Ran `docker compose down`.
10. Recreated PostgreSQL.
11. Verified that the `playground` database survived.
12. Inspected Docker volumes and confirmed that
    `playground_postgres_data` remained after the container was removed.

### Key Insight

Container lifecycle must not be confused with data lifecycle.

PostgreSQL is stateful, so its persistent data should live in storage
that survives container recreation.

### Definition of Done

- [x] Understand stateful vs stateless services.
- [x] Understand why database data should survive container recreation.
- [x] Understand Docker volumes.
- [x] Create a named volume using Docker Compose.
- [x] Mount a volume into PostgreSQL.
- [x] Verify data persistence after `docker compose down`.
- [x] Understand the difference between `down` and `down -v`.
- [x] Inspect Docker volumes.
- [x] Understand the PostgreSQL 18 volume mount requirement.

### Lessons Learned

> Never confuse the lifecycle of compute with the lifecycle of data.

Docker containers can be disposable while persistent data must have
a longer lifecycle.

## Session 7 — Port Publishing & System Boundaries

### Goal

Understand the difference between internal container communication
and exposing services to the host.

### Learned

- Containers on the same Docker network do not need published ports
  to communicate.
- Services communicate internally using service names such as
  `postgres:5432`.
- Port publishing is used when the host or an external client needs
  access to a container.
- Port mapping follows: 
  
  HOST_PORT:CONTAINER_PORT  
  E.g: `15432:5432` means the host connects to port 15432 and 
  Docker forwards traffic to port 5432 inside the container.

- Internal services should not be exposed unnecessarily.
- Minimizing exposed services reduces system attack surface.

### Key Insight

- Docker Network is for internal service communication.
- Port Publishing crosses the system boundary.
- Expose only what actually needs to be exposed.

## Session 8 — First Data Pipeline

### Goal

Build the first end-to-end data ingestion pipeline from CSV to PostgreSQL.

### Learned

- A data pipeline moves data from a source to a destination.
- Row-by-row inserts are simple but can become inefficient at scale.
- Batch size involves a trade-off between throughput and resource usage.
- Ingestion pipelines should be designed to recover safely from failures.
- Idempotency means running the same ingestion multiple times produces the same final state.
- PostgreSQL constraints can help enforce data integrity.
- `ON CONFLICT DO NOTHING` can prevent duplicate inserts.
- Input data should have a lifecycle independent from the application image.
- Bind mounts allow containers to access host datasets at runtime.
- Read-only mounts enforce least privilege.
- Python ingestion can communicate with PostgreSQL through Docker service discovery.

### Architecture

    datasets/orders.csv
            |
            v
    Python Ingestion
            |
            | postgres:5432
            v
       PostgreSQL
            |
            v
      Docker Volume

### Experiments

1. Created `orders.csv`.
2. Mounted the dataset into the ingestion container.
3. Verified that host data changes are immediately visible in the container.
4. Configured the dataset mount as read-only.
5. Verified that writes to `/data` fail with `Read-only file system`.
6. Built a custom Python ingestion image.
7. Connected ingestion to PostgreSQL using the `postgres` service name.
8. Created the `orders` table.
9. Loaded 5 orders from CSV.
10. Ran the ingestion a second time.
11. Verified that the database still contained exactly 5 rows.

### Key Insight

A reliable ingestion pipeline should be safe to run more than once.

Input data, application code, compute, and persistent storage should have
independent lifecycles.

### Definition of Done

- [x] Create a CSV data source.
- [x] Create a Python ingestion service.
- [x] Mount input data into the container.
- [x] Enforce read-only access to the dataset.
- [x] Connect ingestion to PostgreSQL.
- [x] Create the destination table.
- [x] Load data successfully.
- [x] Prevent duplicate records.
- [x] Run ingestion twice.
- [x] Verify idempotent result.

## Session 9 — Pipeline Reliability

### Goal

Make the ingestion pipeline more resilient to temporary dependency failures.

### Learned

- Container started does not mean service ready.
- Docker Healthcheck can verify service readiness.
- `depends_on` with `service_healthy` coordinates startup based on readiness.
- Healthcheck protects startup; it does not handle failures during execution.
- Transient failures may be retried.
- Permanent failures should fail clearly instead of being retried.
- Exponential Backoff increases the delay between retry attempts.
- Retry should be applied only around operations that can reasonably recover.
- PostgreSQL is a long-running service; ingestion is a one-off job.

### Experiments

1. Added PostgreSQL Healthcheck using `pg_isready`.
2. Verified PostgreSQL reached `(healthy)` status.
3. Configured ingestion to depend on `service_healthy`.
4. Verified ingestion waited until PostgreSQL became healthy.
5. Added connection retry to Python ingestion.
6. Added Exponential Backoff: `1s → 2s → 4s → 8s`.
7. Intentionally used an invalid PostgreSQL hostname.
8. Verified retry and backoff behavior.
9. Restored the correct hostname.
10. Verified ingestion succeeded again.

### Key Insight

Reliability requires different protections at different stages:

    Before execution → Healthcheck / Readiness
    During execution → Retry / Backoff
    Permanent error  → Fail clearly

### Definition of Done

- [x] Understand Started vs Ready.
- [x] Add PostgreSQL Healthcheck.
- [x] Verify healthy status.
- [x] Wait for service readiness before ingestion.
- [x] Understand transient vs permanent failures.
- [x] Implement connection retry.
- [x] Implement Exponential Backoff.
- [x] Limit retry attempts.
- [x] Test an intentional connection failure.
- [x] Verify successful recovery.

## Session 10 — Architecture Review & Ingestion Performance

### Goal

Review the current pipeline using quality attributes and compare
row-by-row ingestion with PostgreSQL COPY using real measurements.

### Learned

- A working system is not necessarily a good system.
- Architecture should be evaluated using Quality Attributes.
- Performance decisions should be based on measurement, not assumptions.
- A Baseline provides a reference for evaluating improvements.
- Architectural decisions involve trade-offs.
- PostgreSQL COPY is designed for efficient bulk loading.
- Higher throughput can come with different failure characteristics.
- Failure Granularity describes how much work/data is affected by a failure.
- Atomicity means an operation succeeds completely or is rolled back completely.
- Data Quality, Observability, Security, Reliability, and Performance
  can require different architectural approaches.

### Architecture Review

Current concerns identified:

- Performance — row-by-row INSERT may not scale.
- Data Quality — invalid business data may reach the database.
- Observability — pipeline execution needs operational visibility.
- Security — database credentials should not be hard-coded.

### Benchmark

Dataset:

    100,000 orders

Method A — Row-by-row INSERT:

    Duration:    8.08s
    Throughput:  12,369 rows/sec
    DB rows:     100,000

Method B — PostgreSQL COPY:

    Duration:    0.10s
    Throughput:  988,933 rows/sec
    DB rows:     100,000

COPY achieved approximately 80x higher throughput in this experiment.

### Failure Experiment

Introduced an invalid row into the COPY input:

    amount = ABC

Result:

    COPY failed
    Transaction rolled back
    DB rows = 0

This demonstrated the atomic behavior of the bulk load.

### Trade-off

Row-by-row INSERT:

- Lower throughput.
- Fine-grained processing is easier.
- Easier to handle/reject individual records.

PostgreSQL COPY:

- Very high throughput.
- Efficient bulk loading.
- Strong atomic behavior.
- One invalid record can fail the entire bulk operation.

### Key Insight

There is no universally best solution.

The appropriate solution depends on workload and required Quality Attributes.

Performance improvement must be evaluated together with reliability,
failure behavior, maintainability, data quality, and operational needs.

### Definition of Done

- [x] Review the pipeline using Quality Attributes.
- [x] Identify Performance, Data Quality, Observability, and Security concerns.
- [x] Generate a 100,000-row test dataset.
- [x] Establish row-by-row INSERT baseline.
- [x] Implement PostgreSQL COPY.
- [x] Measure duration and throughput.
- [x] Verify correct row count.
- [x] Compare both ingestion strategies.
- [x] Introduce an intentional bad row.
- [x] Verify COPY rollback behavior.
- [x] Understand Failure Granularity.
- [x] Understand Atomicity.
- [x] Evaluate architectural trade-offs.