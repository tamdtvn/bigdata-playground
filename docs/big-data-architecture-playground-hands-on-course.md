# Big Data Architecture Playground --- Hands-on Course

> **30 sessions + Final Architecture Review**\
> Learning style: **Problem → Prediction → Experiment → Evidence →
> Mental Model → Trade-off → Decision**

## 0. About this course

This is a reconstruction of the Big Data Playground as a **hands-on
course for a new learner**. It is not a chat transcript. Learner answers
and conversational branches have been removed. The goal is that another
learner can build the playground from zero and reproduce the
architectural reasoning.

### Accuracy and reconstruction policy

The session sequence, concepts, measured evidence, architectural
decisions, and major experiments come from the original Playground
learning history. Some original source files from early sessions are no
longer available verbatim. In those places, runnable examples are marked
**Reconstructed Lab Code**: they preserve the experiment and learning
objective but should not be interpreted as byte-for-byte copies of the
historical code.

Recorded measurements are preserved as **course evidence**. A new
learner should expect different timings on different hardware.

### How to study

For every session:

1.  Read **Why this session exists**.
2.  Stop at **Prediction** and answer before running anything.
3.  Execute the lab step by step.
4.  Record your own evidence.
5.  Compare it with the original Playground evidence.
6.  Explain *why* the result happened.
7.  Keep the architecture principle; commands are secondary.

> **Architecture rule:** No technology without a problem, no decision
> without a trade-off, and no claim without evidence.

------------------------------------------------------------------------

# 1. Prerequisites

You need:

-   Git
-   Docker Desktop or Docker Engine
-   Docker Compose v2 (`docker compose`)
-   A terminal
-   A text editor / IDE
-   Internet access for first image/package downloads

Python, PostgreSQL, Spark, and Airflow will run primarily through
containers so the host stays simple.

Check:

``` bash
docker --version
docker compose version
git --version
```

Create the repository:

``` bash
mkdir big-data-playground
cd big-data-playground
git init
```

Initial structure:

``` text
big-data-playground/
├── data/
├── datasets/
├── docker-compose.yml
├── src/
├── experiments/
└── docs/
```

------------------------------------------------------------------------

# PART I --- CONTAINER & DATA FOUNDATIONS

# Session 01 --- Why Containers?

## Goal

Understand the problem Docker solves before learning Docker commands.

## Why this session exists

A program can work on one machine and fail on another because runtime,
libraries, operating-system packages, configuration, and environment
differ.

We want an execution environment that is reproducible.

## Mental model

``` text
Class  → Object
Image  → Container
```

An **image** is a packaged template.\
A **container** is a running instance of that image.

## Prediction

Before running anything:

1.  If we delete a container, must its image disappear?
2.  Can multiple containers be created from one image?
3.  Is a container the same thing as a virtual machine?

Do not continue until you have written your prediction.

## Lab

### Step 1 --- Run the smallest container

``` bash
docker run hello-world
```

What happened conceptually:

``` text
Docker CLI
   ↓
Docker Engine
   ↓
Find image locally?
   ├── No → pull image
   └── Yes
   ↓
Create container
   ↓
Run process
   ↓
Process exits
```

### Step 2 --- Inspect images

``` bash
docker images
```

Look for `hello-world`.

### Step 3 --- Inspect running containers

``` bash
docker ps
```

The container is no longer running because its process already exited.

### Step 4 --- Inspect all containers

``` bash
docker ps -a
```

The stopped container still exists.

### Step 5 --- Run another instance

``` bash
docker run hello-world
docker ps -a
```

One image can create multiple container instances.

### Step 6 --- Remove stopped containers

``` bash
docker container prune
```

Then:

``` bash
docker images
```

The image can remain after containers are removed.

## Evidence to record

  Observation                                          Your evidence
  ---------------------------------------------------- ---------------
  Image exists                                         
  Container can exit                                   
  Stopped container can still exist                    
  Multiple containers can use one image                
  Removing container does not require removing image   

## Architecture lesson

Docker is not valuable because `docker run` is convenient. Its
architectural value is that **execution dependencies become explicit and
reproducible**.

## Trade-off

You gain environment consistency, isolation, and reproducibility, but
introduce image management, container networking, storage boundaries,
and operational concepts.

## Vocabulary

-   Image
-   Container
-   Docker Engine
-   Registry
-   Container lifecycle

## Questions to answer

1.  Explain Image vs Container without using Docker terminology.
2.  Why does `docker ps` differ from `docker ps -a`?
3.  What survives when a container exits?
4.  What problem would still exist if the application image were
    reproducible but its database state lived only inside the container?

------------------------------------------------------------------------

# Session 02 --- Dockerfile, Build Context & Layers

## Goal

Build your own image and understand cache/layers.

## Problem

`hello-world` is somebody else's image. We need a repeatable recipe for
our own application.

## Reconstructed Lab Code

Create:

``` text
src/
└── hello/
    ├── Dockerfile
    └── hello.py
```

`src/hello/hello.py`:

``` python
print("Hello from Big Data Playground")
```

`src/hello/Dockerfile`:

``` dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY hello.py .

CMD ["python", "hello.py"]
```

## Prediction

If only `hello.py` changes, which build steps should Docker be able to
reuse?

## Lab

Build:

``` bash
docker build -t big-data-hello:1.0 ./src/hello
```

Run:

``` bash
docker run --rm big-data-hello:1.0
```

Expected logical output:

``` text
Hello from Big Data Playground
```

Build again without changes:

``` bash
docker build -t big-data-hello:1.0 ./src/hello
```

Observe cached steps.

Now change the message in `hello.py` and rebuild.

## Mental model

``` text
Build Context
   ↓
Dockerfile
   ↓
Layer 1: FROM
Layer 2: WORKDIR
Layer 3: COPY
Layer 4: CMD metadata
   ↓
Image
```

## Experiment --- Cache invalidation

Add a dependency file:

`requirements.txt`

``` text
pandas==2.2.3
```

Compare these two Dockerfile shapes conceptually:

Bad for cache reuse:

``` dockerfile
COPY . .
RUN pip install -r requirements.txt
```

Better:

``` dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
```

Ask why source-code edits should not force dependency installation when
dependencies did not change.

## Questions to answer

1.  What is build context?
2.  Why does instruction ordering influence build speed?
3.  Is an image a running process?
4.  Why is a Dockerfile part of architecture reproducibility?

## Principle

> Put stable dependencies earlier and frequently changing content later
> when that improves cache reuse.

------------------------------------------------------------------------

# Session 03 --- `.dockerignore` and Build Boundaries

## Goal

Control what is allowed into the image build context.

## Problem

Repositories contain files that should not become part of a deployable
artifact: `.git`, logs, IDE state, local output, secrets, datasets,
temporary files.

## Lab

At repository root create `.dockerignore`:

``` text
.git
.gitignore
**/__pycache__
**/*.pyc
.vscode
.idea
logs
tmp
*.log
.env
```

For a service-specific build context, keep a service-local
`.dockerignore` when appropriate.

Build again:

``` bash
docker build -t big-data-hello:1.0 ./src/hello
```

## Security thought experiment

Imagine `.env` contains:

``` text
DB_PASSWORD=super-secret
```

If `COPY . .` is used and `.env` is not ignored, the secret can enter an
image layer even if later deleted.

## Questions to answer

1.  Is `.dockerignore` only a performance feature?
2.  Why is "copy everything, delete later" unsafe for secrets?
3.  What belongs in the deployable unit?
4.  How does a build boundary differ from a repository boundary?

## Principle

> A repository may contain many concerns; a build context should contain
> only what is needed to produce the artifact.

------------------------------------------------------------------------

# Session 04 --- Container Networking

## Goal

Understand why `localhost` is relative to a network namespace.

## Problem

Soon Python must connect to PostgreSQL. If they run in separate
containers, `localhost` inside Python points to Python's container, not
PostgreSQL.

## Lab

Create `docker-compose.yml`:

``` yaml
services:
  app:
    image: python:3.12-slim
    command: ["python", "-c", "import socket; print(socket.gethostname()); print(socket.gethostbyname('db'))"]

  db:
    image: postgres:18
    environment:
      POSTGRES_USER: playground
      POSTGRES_PASSWORD: playground
      POSTGRES_DB: playground
```

Run:

``` bash
docker compose run --rm app
```

The service name `db` resolves on the Compose network.

Inspect:

``` bash
docker network ls
docker compose ps
```

## Mental model

``` text
Host
├── Container app
│   └── localhost = app
└── Container db
    └── localhost = db

app → db:5432
```

## Questions to answer

1.  Why does `localhost:5432` from `app` not mean PostgreSQL?
2.  Why can `db:5432` work without knowing a container IP?
3.  Should application configuration store ephemeral container IP
    addresses?
4.  What is the value of service discovery by stable logical name?

## Principle

> Address dependencies by stable service identity, not ephemeral runtime
> location.

------------------------------------------------------------------------

# Session 05 --- Docker Compose as Runtime Topology

## Goal

Describe a small system as code.

## Problem

Manual commands create hidden operational knowledge.

## Lab

Expand `docker-compose.yml`:

``` yaml
services:
  postgres:
    image: postgres:18
    environment:
      POSTGRES_USER: playground
      POSTGRES_PASSWORD: playground
      POSTGRES_DB: playground
    ports:
      - "5432:5432"

  client:
    image: postgres:18
    environment:
      PGPASSWORD: playground
    command:
      - sh
      - -c
      - |
        sleep 3
        psql -h postgres -U playground -d playground -c "select version();"
    depends_on:
      - postgres
```

Run:

``` bash
docker compose up
```

Stop:

``` bash
docker compose down
```

## Important observation

`depends_on` in its simplest form expresses startup ordering, not
necessarily application readiness. We will fix that in Session 09.

## Questions to answer

1.  What knowledge has moved from terminal commands into Compose?
2.  Are `postgres` and `client` now one process?
3.  Why is a declarative topology easier to reproduce?
4.  What problem remains even after `depends_on`?

## Principle

> Make runtime topology machine-readable, but do not confuse startup
> ordering with readiness.

------------------------------------------------------------------------

# Session 06 --- PostgreSQL Persistence with Volumes

## Goal

Separate data lifecycle from container lifecycle.

## Problem

A database container should be replaceable without losing the database.

## Lab

Update PostgreSQL:

``` yaml
services:
  postgres:
    image: postgres:18
    environment:
      POSTGRES_USER: playground
      POSTGRES_PASSWORD: playground
      POSTGRES_DB: playground
    ports:
      - "5432:5432"
    volumes:
      - playground_postgres_data:/var/lib/postgresql

volumes:
  playground_postgres_data:
```

Start:

``` bash
docker compose up -d postgres
```

Create evidence:

``` bash
docker compose exec postgres \
  psql -U playground -d playground \
  -c "create table if not exists evidence(id int primary key, note text);"

docker compose exec postgres \
  psql -U playground -d playground \
  -c "insert into evidence values (1, 'volume survives container replacement') on conflict do nothing;"
```

Verify:

``` bash
docker compose exec postgres \
  psql -U playground -d playground \
  -c "select * from evidence;"
```

Now:

``` bash
docker compose down
docker compose up -d postgres
```

Query again.

Finally understand the destructive command:

``` bash
docker compose down -v
```

Do not run it unless you intentionally want to delete the named volume.

## Questions to answer

1.  What survives `docker compose down`?
2.  Why should database state not belong to a particular container
    instance?
3.  What does `-v` change?
4.  Which is more disposable: compute or durable state?

## Principle

> Compute instances are replaceable; durable state needs its own
> lifecycle.

------------------------------------------------------------------------

# Session 07 --- Port Mapping & System Boundaries

## Goal

Distinguish internal service ports from host exposure.

## Mental model

``` text
Host localhost:5432
        │
        │ published port
        ▼
PostgreSQL container:5432

Other Compose service
        │
        └──────────────→ postgres:5432
```

## Experiment

Change:

``` yaml
ports:
  - "15432:5432"
```

From the host, PostgreSQL is now exposed at `localhost:15432`.

From another Compose service, it remains:

``` text
postgres:5432
```

## Questions to answer

1.  Why does changing the host port not require changing
    container-to-container configuration?
2.  Does every internal service need a published port?
3.  What attack surface is created by unnecessary host exposure?
4.  Which side of `15432:5432` belongs to the host?

## Principle

> Publish a port only when a consumer outside the container network
> needs it.

------------------------------------------------------------------------

# Session 08 --- First Data Pipeline: CSV → Python → PostgreSQL

## Goal

Create the first real data pipeline and discover idempotency.

## Project structure

``` text
datasets/
└── orders.csv

database/
└── init/
    └── 001-orders.sql

src/
└── ingestion/
    ├── Dockerfile
    ├── requirements.txt
    └── ingest.py
```

## Step 1 --- Create sample data

`datasets/orders.csv`:

``` csv
order_id,customer_id,product,amount,order_date
1,101,Laptop,1200,2026-01-01
2,102,Mouse,25,2026-01-01
3,101,Keyboard,75,2026-01-02
4,103,Monitor,300,2026-01-02
5,104,Dock,150,2026-01-03
```

## Step 2 --- Create schema

`database/init/001-orders.sql`:

``` sql
CREATE TABLE IF NOT EXISTS orders (
    order_id     BIGINT PRIMARY KEY,
    customer_id  BIGINT NOT NULL,
    product      TEXT NOT NULL,
    amount       NUMERIC(12,2) NOT NULL,
    order_date   DATE NOT NULL
);
```

Mount init scripts:

``` yaml
services:
  postgres:
    image: postgres:18
    environment:
      POSTGRES_USER: playground
      POSTGRES_PASSWORD: playground
      POSTGRES_DB: playground
    volumes:
      - playground_postgres_data:/var/lib/postgresql
      - ./database/init:/docker-entrypoint-initdb.d:ro
```

For a clean initialization during the lab:

``` bash
docker compose down -v
docker compose up -d postgres
```

## Step 3 --- Build ingestion

`src/ingestion/requirements.txt`:

``` text
psycopg[binary]==3.2.3
```

`src/ingestion/Dockerfile`:

``` dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ingest.py .

CMD ["python", "ingest.py"]
```

`src/ingestion/ingest.py` (**Reconstructed Lab Code**):

``` python
import csv
import psycopg

conninfo = (
    "host=postgres port=5432 dbname=playground "
    "user=playground password=playground"
)

with psycopg.connect(conninfo) as conn:
    with conn.cursor() as cur:
        with open("/data/orders.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                cur.execute(
                    """
                    INSERT INTO orders(
                        order_id,
                        customer_id,
                        product,
                        amount,
                        order_date
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (order_id) DO NOTHING
                    """,
                    (
                        row["order_id"],
                        row["customer_id"],
                        row["product"],
                        row["amount"],
                        row["order_date"],
                    ),
                )

    conn.commit()

print("Ingestion completed")
```

Compose service:

``` yaml
  ingestion:
    build: ./src/ingestion
    volumes:
      - ./datasets:/data:ro
    depends_on:
      - postgres
```

## Prediction

Run the ingestion twice.

Will PostgreSQL contain **5 rows or 10 rows**?

Write your answer before running.

## Step 4 --- Run

``` bash
docker compose run --rm --build ingestion
```

Query:

``` bash
docker compose exec postgres \
  psql -U playground -d playground \
  -c "select * from orders order by order_id;"
```

Run again:

``` bash
docker compose run --rm ingestion
```

Count:

``` bash
docker compose exec postgres \
  psql -U playground -d playground \
  -c "select count(*) from orders;"
```

Original Playground evidence:

``` text
Run #1 → 5 rows
Run #2 → 5 rows
```

## Step 5 --- Prove the dataset is read-only

``` bash
docker compose run --rm ingestion \
  sh -c "echo test > /data/should-fail.txt"
```

The write should fail because `/data` is mounted `:ro`.

## Mental model

``` text
Retry
  ↓
Same input may be processed again
  ↓
Duplicate side effects?
  ↓
Need safe re-execution
  ↓
Idempotency
```

## Questions to answer

1.  Why is `order_id` the conflict key?
2.  Does `ON CONFLICT DO NOTHING` solve every form of idempotency?
3.  Why is read-only input a useful boundary?
4.  Why will retry become important once orchestration is introduced?

## Principle

> Design pipelines so that re-execution is safe whenever practical.

------------------------------------------------------------------------

# Session 09 --- Reliability: Started ≠ Ready

## Goal

Make dependency readiness explicit and distinguish transient from
permanent failure.

## Step 1 --- Add health check

``` yaml
  postgres:
    image: postgres:18
    environment:
      POSTGRES_USER: playground
      POSTGRES_PASSWORD: playground
      POSTGRES_DB: playground
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U playground -d playground"]
      interval: 2s
      timeout: 2s
      retries: 15
```

Update ingestion:

``` yaml
  ingestion:
    build: ./src/ingestion
    volumes:
      - ./datasets:/data:ro
    depends_on:
      postgres:
        condition: service_healthy
```

Run:

``` bash
docker compose up -d postgres
docker compose ps
```

Observe `healthy`.

## Step 2 --- Add bounded exponential retry

Replace direct connection with a helper (**Reconstructed Lab Code**):

``` python
import time
import psycopg

def connect_with_retry(conninfo, max_attempts=5):
    delay = 1

    for attempt in range(1, max_attempts + 1):
        try:
            return psycopg.connect(conninfo)
        except psycopg.OperationalError as ex:
            print(f"Connection attempt {attempt} failed: {ex}")

            if attempt == max_attempts:
                raise

            print(f"Retrying in {delay}s")
            time.sleep(delay)
            delay *= 2
```

Expected backoff shape:

``` text
attempt 1 → fail → wait 1s
attempt 2 → fail → wait 2s
attempt 3 → fail → wait 4s
attempt 4 → fail → wait 8s
attempt 5 → final failure
```

## Experiment

Temporarily change host to:

``` text
host=postgres-does-not-exist
```

Run ingestion and observe retry.

Then restore `postgres`.

## Questions to answer

1.  Why is `service_started` weaker than `service_healthy`?
2.  Should invalid CSV be retried with exponential backoff?
3.  Should invalid credentials be retried forever?
4.  What property makes a failure plausibly transient?
5.  Why must retry have a limit?

## Principle

> Retry only failures that time may repair, and bound the retry policy.

------------------------------------------------------------------------

# Session 10 --- 100k Benchmark: INSERT vs COPY

## Goal

Measure before optimizing and discover failure granularity.

## Step 1 --- Generate 100k rows

Create `experiments/generate_orders.py`:

``` python
import csv
from datetime import date, timedelta

N = 100_000
products = ["Laptop", "Mouse", "Keyboard", "Monitor", "Dock"]

with open("datasets/orders-100k.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["order_id", "customer_id", "product", "amount", "order_date"])

    start = date(2026, 1, 1)

    for i in range(1, N + 1):
        writer.writerow([
            i,
            1000 + (i % 5000),
            products[i % len(products)],
            10 + (i % 991),
            start + timedelta(days=i % 365),
        ])
```

Run using local Python if available, or:

``` bash
docker run --rm \
  -v "$PWD:/work" \
  -w /work \
  python:3.12-slim \
  python experiments/generate_orders.py
```

PowerShell equivalent:

``` powershell
docker run --rm `
  -v "${PWD}:/work" `
  -w /work `
  python:3.12-slim `
  python experiments/generate_orders.py
```

## Step 2 --- Row-by-row baseline

Instrument the ingestion:

``` python
from time import perf_counter

started = perf_counter()

# ingestion work here

elapsed = perf_counter() - started
print(f"Duration: {elapsed:.2f}s")
print(f"Throughput: {row_count / elapsed:,.0f} rows/s")
```

Original Playground evidence:

``` text
Row INSERT:
Duration   = 8.08 s
Throughput = 12,369 rows/s
```

Your machine will differ.

## Step 3 --- COPY implementation

`src/ingestion/copy_ingest.py` (**Reconstructed Lab Code**):

``` python
import psycopg
from time import perf_counter

conninfo = (
    "host=postgres port=5432 dbname=playground "
    "user=playground password=playground"
)

started = perf_counter()

with psycopg.connect(conninfo) as conn:
    with conn.cursor() as cur:
        with open("/data/orders-100k.csv", "r", encoding="utf-8") as f:
            with cur.copy(
                """
                COPY orders(order_id, customer_id, product, amount, order_date)
                FROM STDIN WITH (FORMAT CSV, HEADER TRUE)
                """
            ) as copy:
                while data := f.read(1024 * 1024):
                    copy.write(data)

elapsed = perf_counter() - started
print(f"Duration: {elapsed:.2f}s")
```

Truncate first:

``` bash
docker compose exec postgres \
  psql -U playground -d playground \
  -c "truncate table orders;"
```

Run COPY variant.

Original Playground evidence:

``` text
COPY:
Duration   = 0.10 s
Throughput = 988,933 rows/s

≈ 80× measured throughput improvement
```

## Step 4 --- Failure granularity experiment

Edit one row around 53,217:

``` csv
53217,....,ABC,....
```

where `ABC` lands in numeric `amount`.

Truncate:

``` bash
docker compose exec postgres \
  psql -U playground -d playground \
  -c "truncate table orders;"
```

Run COPY.

Then:

``` bash
docker compose exec postgres \
  psql -U playground -d playground \
  -c "select count(*) from orders;"
```

Original evidence:

``` text
COPY failed
Final count = 0
```

## Mental model

``` text
Bulk Load
  ├── high throughput
  └── coarse failure boundary

One bad row
  ↓
whole load can fail
  ↓
need validation / staging strategy
```

## Questions to answer

1.  Why did COPY improve throughput so dramatically in this experiment?
2.  Is an 80× result portable to every machine and dataset?
3.  Is "whole load rolls back" a weakness or a useful atomicity
    guarantee?
4.  When would a staging table be useful?
5.  Which Quality Attributes changed besides Performance?

## Principle

> Performance optimizations change failure semantics; benchmark both
> speed and correctness behavior.

------------------------------------------------------------------------

# PART II --- ANALYTICAL STORAGE & DATA LAKE

# Session 11 --- CSV → Parquet: Columnar Storage

## Goal

Understand Parquet by measuring storage and query behavior.

## Dependencies

Create `experiments/requirements.txt`:

``` text
pandas==2.2.3
pyarrow==18.1.0
```

Run experiments in a container:

``` bash
docker run --rm \
  -v "$PWD:/work" \
  -w /work \
  python:3.12-slim \
  sh -c "pip install -q -r experiments/requirements.txt && python experiments/session11_parquet.py"
```

## Lab code

`experiments/session11_parquet.py` (**Reconstructed Lab Code**):

``` python
from pathlib import Path
from time import perf_counter

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

csv_path = Path("datasets/orders-100k.csv")
parquet_path = Path("experiments/orders-100k.parquet")

df = pd.read_csv(csv_path)

table = pa.Table.from_pandas(df, preserve_index=False)
pq.write_table(table, parquet_path, row_group_size=25_000)

pf = pq.ParquetFile(parquet_path)

print("rows:", pf.metadata.num_rows)
print("row groups:", pf.metadata.num_row_groups)
print("csv bytes:", csv_path.stat().st_size)
print("parquet bytes:", parquet_path.stat().st_size)

for i in range(pf.metadata.num_row_groups):
    rg = pf.metadata.row_group(i)
    print("row group", i, "rows", rg.num_rows)
```

Original evidence:

``` text
CSV     ≈ 2.54 MB
Parquet ≈ 0.62 MB
Reduction ≈ 76%
Row groups = 4
Rows/group = 25,000
```

## Inspect metadata

Add:

``` python
schema = pf.schema_arrow
order_idx = schema.get_field_index("order_id")

for i in range(pf.metadata.num_row_groups):
    col = pf.metadata.row_group(i).column(order_idx)
    stats = col.statistics
    print(i, stats.min, stats.max)
```

## Query benchmark

``` python
started = perf_counter()
csv_df = pd.read_csv(csv_path)
csv_result = csv_df.loc[csv_df["order_id"] > 80_000, ["amount"]]
csv_elapsed = perf_counter() - started

started = perf_counter()
pq_result = pq.read_table(
    parquet_path,
    columns=["amount"],
    filters=[("order_id", ">", 80_000)],
)
pq_elapsed = perf_counter() - started

print("CSV:", csv_elapsed)
print("Parquet:", pq_elapsed)
```

Original Playground evidence on the small dataset:

``` text
Parquet ≈ 0.430843 s
CSV     ≈ 0.067223 s
```

CSV was faster.

## Prediction questions

1.  Why can CSV beat Parquet on a tiny workload?
2.  Which columns does the Parquet query logically need?
3.  Why can earlier row groups be excluded for `order_id > 80000`?
4.  What is the **crossover point**?

## Principle

> Parquet does not promise "always faster." It creates opportunities to
> avoid unnecessary I/O and decoding.

------------------------------------------------------------------------

# Session 12 --- Partitioning & the Small Files Problem

## Goal

Choose partition granularity from workload.

## Step 1 --- Generate deterministic 1M orders

`experiments/session12_generate.py`:

``` python
from pathlib import Path
import numpy as np
import pandas as pd

N = 1_000_000
rng = np.random.default_rng(42)

dates = pd.date_range("2026-01-01", "2026-12-31", freq="D")

df = pd.DataFrame({
    "order_id": np.arange(1, N + 1, dtype=np.int64),
    "customer_id": rng.integers(1, 50_001, size=N),
    "product": rng.choice(["Laptop", "Mouse", "Keyboard", "Monitor", "Dock"], size=N),
    "amount": rng.integers(10, 1001, size=N),
    "order_date": rng.choice(dates, size=N),
})

df["order_date"] = pd.to_datetime(df["order_date"])
df["order_month"] = df["order_date"].dt.strftime("%Y-%m")
df["order_day"] = df["order_date"].dt.strftime("%Y-%m-%d")

Path("experiments/partitioning").mkdir(parents=True, exist_ok=True)

df.to_parquet("experiments/partitioning/non_partitioned.parquet", index=False)

df.to_parquet(
    "experiments/partitioning/by_month",
    partition_cols=["order_month"],
    index=False,
)

df.to_parquet(
    "experiments/partitioning/by_day",
    partition_cols=["order_day"],
    index=False,
)
```

## Prediction

Rank non-partitioned, month, day for:

-   one-day query;
-   August query;
-   full-year query.

Also predict write cost.

## Original evidence

Write times:

``` text
non-partitioned = 0.236 s
by month        = 0.591 s
by day          = 4.726 s
```

Daily query:

``` text
non-partitioned = 0.030599 s
month           = 0.008411 s
day             = 0.004164 s
```

August query:

``` text
non-partitioned = 0.043685 s
month           = 0.007643 s
day             = 0.054943 s
```

Year query:

``` text
non-partitioned = 0.026792 s
month           = 0.024896 s
day             = 0.571435 s
```

## Why day can lose

A day query can prune aggressively. But a full-year query may need to
discover/open hundreds of small files/partitions.

That is the **Small Files Problem**.

## Correctness experiment

Imagine:

``` text
order_date = 2026-08-28
physical partition = order_day=2026-08-27
```

A query that prunes to `order_day=2026-08-28` may never see that row.

Therefore:

> Physical partition membership must agree with the business partition
> key.

## Decision

For the observed workload, choose monthly partitioning.

This became **ADR-002** in the Playground.

## Questions to answer

1.  Why is the daily layout not the overall winner?
2.  What workload change would justify revisiting monthly partitioning?
3.  Why is partitioning both a performance and correctness concern?
4.  Why does high partition cardinality create metadata/filesystem
    overhead?

## Principle

> Partitioning does not make queries fast; pruning does. Partition
> strategy must follow access patterns.

------------------------------------------------------------------------

# Session 13 --- Predicate Pushdown, Row-group Statistics & Physical Ordering

## Goal

Prove that pushdown, statistics, and skipping are different concepts.

## Lab code

`experiments/session13_pushdown.py`:

``` python
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

N = 1_000_000
rng = np.random.default_rng(42)

df = pd.DataFrame({
    "order_id": np.arange(1, N + 1, dtype=np.int64),
    "amount": rng.integers(10, 1001, size=N),
})

root = Path("experiments/pushdown")
root.mkdir(parents=True, exist_ok=True)

unsorted_path = root / "orders.parquet"
sorted_path = root / "orders_sorted_by_amount.parquet"

pq.write_table(
    pa.Table.from_pandas(df, preserve_index=False),
    unsorted_path,
    row_group_size=100_000,
)

pq.write_table(
    pa.Table.from_pandas(df.sort_values("amount"), preserve_index=False),
    sorted_path,
    row_group_size=100_000,
)
```

## Inspect statistics

``` python
def show_stats(path, column):
    pf = pq.ParquetFile(path)
    idx = pf.schema_arrow.get_field_index(column)

    print(f"\n{path} / {column}")

    for i in range(pf.metadata.num_row_groups):
        stats = pf.metadata.row_group(i).column(idx).statistics
        print(i, stats.min, stats.max)

show_stats(unsorted_path, "order_id")
show_stats(unsorted_path, "amount")
show_stats(sorted_path, "order_id")
show_stats(sorted_path, "amount")
```

## Compare filtering after read vs filter pushdown

``` python
def after_read(path, column, threshold):
    start = perf_counter()
    table = pq.read_table(path, columns=[column])
    df = table.to_pandas()
    result = df[df[column] > threshold]
    return len(result), perf_counter() - start

def pushed(path, column, threshold):
    start = perf_counter()
    table = pq.read_table(
        path,
        columns=[column],
        filters=[(column, ">", threshold)],
    )
    return table.num_rows, perf_counter() - start
```

## Original evidence --- unsorted

`order_id > 900000`:

``` text
after read = 0.062166 s
pushdown   = 0.006015 s
```

`amount > 900`:

``` text
after read = 0.028452 s
pushdown   = 0.027473 s
```

## Prediction

Why does amount barely improve?

Inspect row-group min/max before answering.

## Sort by amount and repeat

Original evidence:

`order_id > 900000`:

``` text
after read = 0.068777 s
pushdown   = 0.021306 s
```

`amount > 900`:

``` text
after read = 0.028382 s
pushdown   = 0.006205 s
```

## Mental model

``` text
Predicate Pushdown = mechanism
Row-group Statistics = metadata
Data Skipping = benefit when metadata can reject blocks
```

## Questions to answer

1.  Does `PushedFilters` prove physical skipping occurred?
2.  Why did sorting by amount help the amount predicate?
3.  Why did the order-id access pattern weaken?
4.  What is the trade-off of physical ordering?

## Principle

> Physical ordering optimizes access patterns, not "the dataset" in the
> abstract.

------------------------------------------------------------------------

# Session 14 --- Build a Data Lake: Raw → Cleaned → Curated

## Goal

Separate source truth, trusted data, and business-ready outputs.

## Target structure

``` text
data/
└── lake/
    ├── raw/
    │   └── orders/
    │       └── orders.csv
    ├── cleaned/
    │   └── orders/
    │       └── orders.parquet
    └── curated/
        ├── daily_revenue/
        │   └── revenue.parquet
        └── monthly_revenue/
            └── revenue.parquet
```

Keep benchmark files under:

``` text
experiments/
```

because:

> Experiment output ≠ business data product.

## Step 1 --- Raw

Copy the source CSV unchanged:

``` bash
mkdir -p data/lake/raw/orders
cp datasets/orders-100k.csv data/lake/raw/orders/orders.csv
```

On PowerShell:

``` powershell
New-Item -ItemType Directory -Force data/lake/raw/orders
Copy-Item datasets/orders-100k.csv data/lake/raw/orders/orders.csv
```

## Step 2 --- Cleaned builder

`src/processing/build_cleaned_orders.py` (**Reconstructed Lab Code**):

``` python
from pathlib import Path
import pandas as pd

RAW = Path("/lake/raw/orders/orders.csv")
OUT = Path("/lake/cleaned/orders/orders.parquet")

required = {
    "order_id",
    "customer_id",
    "product",
    "amount",
    "order_date",
}

df = pd.read_csv(RAW)

missing = required - set(df.columns)
if missing:
    raise ValueError(f"Missing columns: {sorted(missing)}")

if df[list(required)].isnull().any().any():
    raise ValueError("Required data contains nulls")

df["order_id"] = pd.to_numeric(df["order_id"], errors="raise")
df["customer_id"] = pd.to_numeric(df["customer_id"], errors="raise")
df["amount"] = pd.to_numeric(df["amount"], errors="raise")
df["order_date"] = pd.to_datetime(df["order_date"], errors="raise")

if (df["amount"] < 0).any():
    raise ValueError("Negative amount")

if df["order_id"].duplicated().any():
    raise ValueError("Duplicate order_id")

OUT.parent.mkdir(parents=True, exist_ok=True)
df.to_parquet(OUT, index=False)

print(f"Published cleaned rows={len(df)} -> {OUT}")
```

## Step 3 --- Curated builders

`src/processing/build_revenue_curated.py`:

``` python
from pathlib import Path
import pandas as pd

INPUT = Path("/lake/cleaned/orders/orders.parquet")
DAILY = Path("/lake/curated/daily_revenue/revenue.parquet")
MONTHLY = Path("/lake/curated/monthly_revenue/revenue.parquet")

df = pd.read_parquet(INPUT)
df["order_date"] = pd.to_datetime(df["order_date"])

daily = (
    df.groupby(df["order_date"].dt.date, as_index=False)["amount"]
      .sum()
      .rename(columns={"order_date": "date", "amount": "revenue"})
)

monthly = (
    df.assign(month=df["order_date"].dt.to_period("M").astype(str))
      .groupby("month", as_index=False)["amount"]
      .sum()
      .rename(columns={"amount": "revenue"})
)

DAILY.parent.mkdir(parents=True, exist_ok=True)
MONTHLY.parent.mkdir(parents=True, exist_ok=True)

daily.to_parquet(DAILY, index=False)
monthly.to_parquet(MONTHLY, index=False)

print("Curated outputs published")
```

## Step 4 --- Processing container

`src/processing/requirements.txt`:

``` text
pandas==2.2.3
pyarrow==18.1.0
```

`src/processing/Dockerfile`:

``` dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
```

Compose:

``` yaml
  processing:
    build: ./src/processing
    volumes:
      - ./data/lake:/lake
```

Run:

``` bash
docker compose run --rm processing python build_cleaned_orders.py
docker compose run --rm processing python build_revenue_curated.py
```

## Failure experiment

Change one raw `amount` to `ABC`.

Run cleaned again.

Expected:

``` text
ValueError / conversion failure
```

Now inspect the old cleaned output.

Important discovery:

> A failed new build does not automatically invalidate or remove
> yesterday's output.

This creates a **stale data risk**.

## Candidate future solution --- not yet implemented

``` text
write temporary
   ↓
validate
   ↓
atomic replace/publish
```

## Questions to answer

1.  Why keep Raw if Cleaned exists?
2.  Why should Cleaned reject invalid numeric data instead of silently
    coercing it?
3.  Why is an existing file not proof that the latest run succeeded?
4.  What is reprocessability?
5.  What is the difference between a zone and a separate physical
    system?

## Principle

> Preserve source truth, validate before trust, publish only valid data.

------------------------------------------------------------------------

# Session 15 --- Review: When Does Scale-out Become Necessary?

## Goal

Create the decision gate before distributed processing.

## Scenario

Assume a production-like batch has:

-   1 TB input
-   optimized single-machine duration: 3 hours
-   required SLA: 30 minutes

## Decision worksheet

Before choosing Spark, fill this:

``` text
Current duration:
Required duration:
Unnecessary I/O already reduced?:
Partition pruning available?:
Column pruning available?:
Predicate pushdown available?:
Scale-up tested?:
Remaining bottleneck:
Evidence:
```

## Questions

1.  If the job takes 20 minutes and SLA is 30, what problem would Spark
    solve?
2.  If the job takes three hours after reasonable optimization, what
    Quality Attribute is violated?
3.  What is the operational cost of scale-out?
4.  Is "1 TB" enough evidence by itself?

## Decision model

``` text
Workload
  ↓
Efficient format/layout
  ↓
Process less
  ↓
Measure vs SLA
  ↓
Optimize / Scale Up
  ↓
Still insufficient?
  ├── No → stop
  └── Yes → evaluate Scale Out
```

## Principle

> Dataset size is context. An unmet Quality Attribute is a reason to
> act.

------------------------------------------------------------------------

# PART III --- DISTRIBUTED PROCESSING

# Session 16 --- Partition → Task → Worker

## Goal

Understand distributed computation without Spark vocabulary first.

## Mental experiment

Suppose 1 TB is split into four independent 250 GB partitions.

``` text
Partition 1 → Worker A
Partition 2 → Worker B
Partition 3 → Worker C
Partition 4 → Worker D
```

If the work is independent, it may run in parallel.

But total duration is not automatically divided by four because of:

-   serial work;
-   startup/coordination overhead;
-   uneven partition sizes;
-   I/O bottlenecks;
-   network movement.

## Hands-on mini experiment

Create `experiments/session16_parallel.py`:

``` python
from concurrent.futures import ProcessPoolExecutor
from time import perf_counter, sleep

def work(partition):
    started = perf_counter()
    sleep(2)
    return partition, perf_counter() - started

if __name__ == "__main__":
    started = perf_counter()

    with ProcessPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(work, range(4)))

    print(results)
    print("wall clock:", perf_counter() - started)
```

Run:

``` bash
docker run --rm \
  -v "$PWD:/work" \
  -w /work \
  python:3.12-slim \
  python experiments/session16_parallel.py
```

Compare conceptually with running four 2-second operations sequentially.

## Questions

1.  Why is wall-clock time not the sum of all task durations under
    parallel execution?
2.  What happens if one partition sleeps 20 seconds while others sleep
    2?
3.  What happens if you create 100,000 tiny tasks?
4.  How does a processing partition differ from a storage partition?

## Principle

> Processing partitions create parallelism boundaries --- and later
> recovery boundaries.

------------------------------------------------------------------------

# Session 17 --- Spark Fundamentals: Driver, Executors, Jobs, Stages, Tasks

## Goal

Map the generic model onto Spark.

## Add Spark service

``` yaml
  spark:
    image: apache/spark:4.0.1
    user: root
    working_dir: /work
    volumes:
      - ./data/lake:/lake
      - ./experiments:/work
```

## First Spark program

`experiments/session17_spark.py`:

``` python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = (
    SparkSession.builder
    .appName("big-data-playground-session17")
    .master("local[4]")
    .getOrCreate()
)

df = spark.read.parquet("/lake/cleaned/orders/orders.parquet")

print("rows =", df.count())
print("processing partitions =", df.rdd.getNumPartitions())

filtered = (
    df.filter(F.col("order_id") > 900_000)
      .select("order_id", "amount")
)

filtered.explain("formatted")
print("result rows =", filtered.count())

spark.stop()
```

Run:

``` bash
docker compose run --rm spark \
  /opt/spark/bin/spark-submit /work/session17_spark.py
```

## Evidence to inspect

Look in the physical plan for concepts such as:

``` text
PushedFilters
ReadSchema
```

Do not overclaim: pushed filters show that Spark communicated a filter
to the Parquet reader. They do not alone prove how many row groups were
physically skipped.

## Mental model

``` text
Spark Application
  ↓
Driver
  ↓
Job
  ↓
Stage
  ↓
Task per processing partition
  ↓
Executor / worker thread
```

In `local[4]`, this is still one machine. The point is to learn the
execution model.

## Questions

1.  Is `local[4]` a four-machine cluster?
2.  Why can a Parquet file with ten row groups result in a different
    number of Spark partitions?
3.  What is lazy evaluation?
4.  Which operations trigger actions?
5.  Why is `explain()` architectural evidence?

## Principle

> Learn the execution model locally before paying the operational cost
> of a real cluster.

------------------------------------------------------------------------

# Session 18 --- Shuffle: When Related Data Must Meet

## Goal

See why global aggregation creates data movement.

## Lab

`experiments/session18_shuffle.py`:

``` python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = (
    SparkSession.builder
    .appName("shuffle-experiment")
    .master("local[4]")
    .config("spark.sql.shuffle.partitions", "8")
    .getOrCreate()
)

df = spark.read.parquet("/lake/cleaned/orders/orders.parquet")

result = (
    df.groupBy("product")
      .agg(
          F.sum("amount").alias("revenue"),
          F.count("*").alias("orders"),
      )
)

result.explain("formatted")
result.show(truncate=False)

spark.stop()
```

Run:

``` bash
docker compose run --rm spark \
  /opt/spark/bin/spark-submit /work/session18_shuffle.py
```

## Evidence

Search the plan for an exchange similar to:

``` text
Exchange hashpartitioning(product, ...)
```

The exact final partition count may be changed by Adaptive Query
Execution, so treat configuration as intent, not proof of runtime
behavior.

## Mental model

``` text
Partition A: Laptop, Mouse
Partition B: Laptop, Dock
Partition C: Mouse, Dock

Need global Laptop total
       ↓
Laptop records/partials must meet
       ↓
Shuffle
```

Spark can often do partial aggregation before shuffle:

``` text
many rows
  ↓
local partial aggregate
  ↓
smaller intermediate data
  ↓
shuffle
  ↓
final aggregate
```

## Questions

1.  Why is `groupBy` usually a wide dependency?
2.  Why can partial aggregation reduce network/data movement?
3.  Why is shuffle often more expensive than a narrow map/filter?
4.  What is the relationship between shuffle and Stage boundary?

## Principle

> Reduce data before moving data whenever possible.

------------------------------------------------------------------------

# Session 19 --- Failure, Retry & Lineage

## Goal

Observe task-level retry.

## Lab

`experiments/session19_retry.py` (**Reconstructed Lab Code**):

``` python
from pyspark import TaskContext
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("retry-experiment")
    .master("local[4,2]")
    .getOrCreate()
)

sc = spark.sparkContext

def process_partition(index, rows):
    ctx = TaskContext.get()
    attempt = ctx.attemptNumber()

    print(f"partition={index} attempt={attempt}")

    if index == 1 and attempt == 0:
        raise RuntimeError("Intentional failure for partition 1 attempt 0")

    count = sum(1 for _ in rows)
    yield (index, attempt, count)

rdd = sc.parallelize(range(100), 4)

result = (
    rdd.mapPartitionsWithIndex(process_partition)
       .collect()
)

print(result)

spark.stop()
```

Run:

``` bash
docker compose run --rm spark \
  /opt/spark/bin/spark-submit /work/session19_retry.py
```

The `local[4,2]` form allows task failure attempts in the local
experiment.

## Original evidence

The successful final results demonstrated:

``` text
Partition 0 → attempt 0
Partition 1 → attempt 1
Partition 2 → attempt 0
Partition 3 → attempt 0
```

The whole job did not need to recompute every successful partition.

## Mental model

``` text
Transformation lineage
      ↓
recipe for recomputation

Failed partition/task
      ↓
retry smallest practical unit
```

## Questions

1.  What does the second number in `local[4,2]` help demonstrate?
2.  Why is lineage different from storing every intermediate result?
3.  What changes when a failure occurs after a shuffle?
4.  Why does recovery granularity matter to cost?

## Principle

> Recovery should happen at the smallest practical unit of failure.

------------------------------------------------------------------------

# Session 20 --- Distributed Processing Architecture Review

## Goal

Decide when Spark belongs in an architecture.

## Architecture exercise

For each scenario, answer **Use Spark? Not yet? Need evidence?**

### Scenario A

``` text
Data: 5 GB
Duration: 40 s
SLA: 5 min
Frequency: once/day
```

### Scenario B

``` text
Data: 1 TB
Duration after optimization: 3 h
SLA: 30 min
Partitionable workload: yes
```

### Scenario C

``` text
Data: 5 TB
Query only needs one monthly partition and two columns
Current implementation reads everything
```

## Questions

1.  Which scenario first needs "process less" rather than "add compute"?
2.  What is a straggler?
3.  How does skew reduce parallel efficiency?
4.  Why does Amdahl's Law matter even with many workers?
5.  What would you measure before approving a cluster?

## Principle

> Do not ask "Is this Big Data?" Ask "Which measured bottleneck will
> distributed processing solve?"

------------------------------------------------------------------------

# PART IV --- ORCHESTRATION FOUNDATIONS

# Session 21 --- Why Orchestration?

## Goal

Discover orchestration from coordination complexity.

## Current manual pipeline

``` bash
docker compose run --rm processing python build_cleaned_orders.py
docker compose run --rm processing python build_revenue_curated.py
```

The operator knows:

-   cleaned must succeed first;
-   curated runs after cleaned;
-   failures need attention;
-   schedules are manual;
-   retries are manual.

That is **execution knowledge in a human head**.

## Dependency exercise

Suppose:

``` text
A = extract source 1     10m
B = clean source 1       20m
C = extract source 2     10m
D = clean source 2       20m
E = combine              20m
F = publish               3m
```

If A→B and C→D are independent branches, they may run concurrently
before E.

A naive sequential procedure can waste time.

## Questions

1.  Which edges are "must wait" dependencies?
2.  Which tasks "may run" concurrently?
3.  Who currently knows those rules?
4.  What happens when the operator is absent?
5.  Does adding an orchestrator make the transformations themselves
    faster?

## Principle

> Orchestration is justified when coordination becomes a system
> responsibility.

------------------------------------------------------------------------

# Session 22 --- DAG, State & Critical Path

## Goal

Represent workflow dependencies as a Directed Acyclic Graph.

## Build a tiny DAG simulator

`experiments/session22_dag.py`:

``` python
from collections import defaultdict, deque

dependencies = {
    "A": [],
    "B": ["A"],
    "C": [],
    "D": ["C"],
    "E": ["B", "D"],
    "F": ["E"],
}

indegree = {task: len(deps) for task, deps in dependencies.items()}
children = defaultdict(list)

for task, deps in dependencies.items():
    for dep in deps:
        children[dep].append(task)

ready = deque([t for t, d in indegree.items() if d == 0])
order = []

while ready:
    task = ready.popleft()
    order.append(task)

    for child in children[task]:
        indegree[child] -= 1
        if indegree[child] == 0:
            ready.append(child)

print("One valid topological order:", order)
```

Run:

``` bash
docker run --rm \
  -v "$PWD:/work" -w /work \
  python:3.12-slim \
  python experiments/session22_dag.py
```

## Critical path

Given durations, compute path totals. A valid topological order is not
the same as the critical path.

Original course example identified:

``` text
A → B → D → F = 60 minutes
```

for its specific dependency graph/durations.

## State model

``` text
WAITING
  ↓ dependencies satisfied
READY
  ↓ worker starts
RUNNING
  ├── SUCCESS
  └── FAILED
```

## Questions

1.  Why can a DAG not contain a cycle?
2.  What does topological ordering tell you?
3.  What does it *not* tell you?
4.  Why should optimization focus on the critical path?
5.  Can a long task outside the critical path be optimized without
    changing total completion time?

## Principle

> Optimize the work that actually constrains completion.

------------------------------------------------------------------------

# Session 23 --- Scheduling, Data Interval, Retry & Backfill

## Goal

Separate wall-clock execution from business time.

## Problem

Suppose a daily revenue job executes:

``` text
2026-09-13 01:00
```

but represents:

``` text
business date = 2026-09-12
```

If processing uses `datetime.now()`, historical re-execution becomes
ambiguous.

## Reconstructed date-aware processing contract

``` python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--business-date", required=True)
args = parser.parse_args()

print(f"Processing logical date: {args.business_date}")
```

Run:

``` bash
python job.py --business-date 2026-09-12
```

Desired output contract:

``` text
data/lake/curated/daily_revenue/date=2026-09-12/revenue.parquet
```

## Recovery reasoning

``` text
Failure
  ↓
Retry same logical scope
  ↓
Idempotent re-execution
  ↓
Validate
  ↓
Atomic publish
```

## Questions

1.  Why is `datetime.now()` dangerous for historical reprocessing?
2.  What exactly should remain the same across retries?
3.  How is backfill different from retry?
4.  Why should output partition align with logical processing scope?
5.  What race condition exists if two runs publish the same date?

## Principle

> Time is part of the execution contract, not just a timestamp in a
> scheduler.

------------------------------------------------------------------------

# Session 24 --- Observability: State, Logs, Metrics, History

## Goal

Create evidence that helps answer "what happened?"

## Instrument a processing step

Add structured-ish logs:

``` python
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

started = time.perf_counter()

logging.info("BUILD_CLEANED started input=%s", RAW)

try:
    # processing
    logging.info("BUILD_CLEANED success rows=%s output=%s", len(df), OUT)
except Exception:
    logging.exception("BUILD_CLEANED failed")
    raise
finally:
    logging.info(
        "BUILD_CLEANED duration_seconds=%.3f",
        time.perf_counter() - started,
    )
```

## Evidence model

``` text
State   → WHAT happened?
Logs    → WHY / detailed sequence?
Metrics → HOW MUCH / HOW LONG / HOW OFTEN?
History → Is behavior changing over time?
```

## Thought experiment

Runs are all `SUCCESS`, but duration changes:

``` text
Day 1: 10m
Day 2: 12m
Day 3: 16m
Day 4: 21m
Day 5: 25m
SLA:   30m
```

The system is currently successful but trending toward a performance
problem.

## Questions

1.  Why is SUCCESS insufficient for health?
2.  Is duration itself a metric?
3.  What execution boundaries should carry duration?
4.  Why does a run ID/correlation ID reduce diagnostic search space?
5.  How would you distinguish symptom, impact, and root cause?

## Principle

> Measure at meaningful execution boundaries so that failure and cost
> can be localized progressively.

------------------------------------------------------------------------

# Session 25 --- Orchestration Architecture Review & Root Cause

## Goal

Decide whether orchestration is justified and practice evidence-based
diagnosis.

## Onion model

``` text
System symptom
  ↓
Pipeline
  ↓
Task
  ↓
Attempt
  ↓
Operation
  ↓
Evidence
  ↓
Actionable root cause
```

## Diagnostic scenario

Observed:

``` text
Pipeline duration:
10m → 12m → 16m → 21m → 25m
```

Do not immediately claim:

``` text
Root cause = performance degradation
```

Performance degradation is the observed problem.

Possible impact:

``` text
SLA violation
```

A root cause requires deeper evidence, e.g. pruning disabled, source
size changed, skew increased, dependency latency increased.

## Questions

1.  When should root-cause analysis stop?
2.  Is "CPU high" always a root cause?
3.  Why can Five Whys be a path through a causal graph rather than a
    universal fixed count?
4.  What is the difference between observed evidence and interpretation?
5.  What coordination problem would justify a real orchestrator now?

## Principle

> Localize first, diagnose second; stop when the cause is actionable and
> evidence-supported for the current scope.

------------------------------------------------------------------------

# PART V --- AIRFLOW WALKING SKELETON

# Session 26 --- Evaluate Airflow, Prefect, Dagster from Requirements

## Goal

Choose an orchestration hypothesis from requirements.

## Requirements

The Playground needs:

-   dependency;
-   scheduling;
-   state;
-   retry;
-   backfill;
-   observability;
-   local/Docker-friendly learning environment.

## Hard constraint vs weighted criterion

Example:

``` text
Hard constraint:
- must run locally in Docker for the course

Weighted criteria:
- concept transparency
- ecosystem maturity
- Python integration
- operational complexity
- fit for batch DAGs
```

## Evaluation worksheet

  Criterion                Weight   Airflow   Prefect   Dagster
  ---------------------- -------- --------- --------- ---------
  Batch DAG fit                                       
  Scheduling                                          
  Retry/state/history                                 
  Backfill                                            
  Docker learning path                                
  Operational cost                                    
  Ecosystem maturity                                  

Do not fill the table from popularity alone. Record evidence/reason for
every score if you use scoring.

## Playground hypothesis

Airflow was selected as the **provisional hypothesis** because the
course needed a transparent batch-DAG model and the required
capabilities.

The decision was not yet final.

## Questions

1.  Why not build a custom orchestrator?
2.  What is the difference between hard constraint and weighted
    criterion?
3.  Why should the PoC happen before the ADR is accepted?
4.  What evidence would falsify the Airflow hypothesis?

## Principle

> Technology selection is a hypothesis until runtime evidence supports
> the decision.

------------------------------------------------------------------------

# Session 27 --- First Real Airflow DAG

## Goal

Prove dependency semantics with a real orchestrator.

## Directory structure

``` text
airflow/
├── Dockerfile
└── dags/
    └── big_data_playground.py

data/
└── lake/

src/
└── processing/
    ├── build_cleaned_orders.py
    └── build_revenue_curated.py
```

## Airflow image

`airflow/Dockerfile` (**Reconstructed Lab Code**):

``` dockerfile
FROM apache/airflow:3.3.1

USER airflow

RUN pip install --no-cache-dir \
    pandas==2.2.3 \
    pyarrow==18.1.0
```

## Compose service

A minimal learning setup can use Airflow standalone:

``` yaml
  airflow:
    build: ./airflow
    command: ["airflow", "standalone"]
    ports:
      - "8080:8080"
    volumes:
      - ./airflow/dags:/opt/airflow/dags
      - ./src/processing:/opt/playground/processing:ro
      - ./data/lake:/lake
```

> This is a learning deployment, not a production Airflow topology.

Start:

``` bash
docker compose up -d --build airflow
docker compose logs -f airflow
```

The standalone startup log provides initial UI credentials.

## DAG

`airflow/dags/big_data_playground.py` (**Reconstructed Lab Code**):

``` python
from datetime import datetime
import subprocess

from airflow.sdk import dag, task

@dag(
    dag_id="big_data_playground",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
)
def big_data_playground():

    @task
    def build_cleaned_orders():
        subprocess.run(
            [
                "python",
                "/opt/playground/processing/build_cleaned_orders.py",
            ],
            check=True,
        )

    @task
    def build_revenue_curated():
        subprocess.run(
            [
                "python",
                "/opt/playground/processing/build_revenue_curated.py",
            ],
            check=True,
        )

    cleaned = build_cleaned_orders()
    curated = build_revenue_curated()

    cleaned >> curated

big_data_playground()
```

## Why `check=True` matters

``` text
processing exits 0
  ↓
Airflow task SUCCESS

processing exits non-zero
  ↓
subprocess raises
  ↓
Airflow task FAILED
  ↓
downstream blocked
```

This is the execution contract between orchestration and processing.

## Experiment A --- Dependency

Trigger the DAG in UI or CLI:

``` bash
docker compose exec airflow \
  airflow dags trigger big_data_playground
```

Observe:

``` text
build_cleaned_orders
        ↓
build_revenue_curated
```

Original evidence:

``` text
cleaned duration ≈ 3.136 s
curated duration ≈ 0.647 s
```

## Experiment B --- Code order ≠ execution order

Create two temporary tasks, both sleeping ten seconds, and **remove the
dependency**.

Example:

``` python
import time

@task
def task_a():
    time.sleep(10)

@task
def task_b():
    time.sleep(10)

task_a()
task_b()
```

Trigger.

Original experiment showed both started in the same second.

Therefore:

> Python source order did not define workflow dependency.

## Control Plane vs Data Plane

``` text
Airflow
WHEN / ORDER / STATE / RETRY
          │
          ▼
Processing scripts
READ / VALIDATE / TRANSFORM / WRITE
```

## Questions

1.  Why not mount Docker socket and make Airflow control Docker directly
    for this small lab?
2.  Why can logical separation exist without a separate container per
    task?
3.  What does `cleaned >> curated` encode that humans previously
    remembered?
4.  Why is output existence not the same as data correctness?

## Principle

> Move execution knowledge from human memory into machine-readable
> dependencies.

------------------------------------------------------------------------

# Session 28 --- Scheduling, Retry & Backfill in Airflow

## Goal

Prove three capabilities and expose the missing business-time contract.

## Experiment A --- Scheduling

Temporarily change:

``` python
schedule="*/5 * * * *"
```

Restart/refresh the DAG and wait.

Observe a scheduler-created run rather than a manual run.

## Experiment B --- Retry

Create `airflow/dags/retry_experiment.py`:

``` python
from datetime import datetime, timedelta
from airflow.sdk import dag, task

@dag(
    dag_id="retry_experiment",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
)
def retry_experiment():

    @task(
        retries=2,
        retry_delay=timedelta(seconds=5),
    )
    def transient_task(**context):
        try_number = context["ti"].try_number
        print(f"try_number={try_number}")

        if try_number == 1:
            raise RuntimeError("Intentional transient failure")

        print("Success")

    transient_task()

retry_experiment()
```

Depending on Airflow API/runtime context details, Task SDK context
access can differ; if needed use the runtime's documented
current-context helper. The learning contract is:

``` text
retries=2
=
1 initial attempt
+
maximum 2 additional attempts
```

Original experiment recovered on Try 2.

## Experiment C --- Backfill

Create a small scheduled daily DAG whose task prints logical-time
context.

Conceptual DAG:

``` python
from datetime import datetime
from airflow.sdk import dag, task

@dag(
    dag_id="backfill_experiment",
    schedule="@daily",
    start_date=datetime(2026, 9, 1),
    catchup=False,
)
def backfill_experiment():

    @task
    def show_context(**context):
        print("run_id =", context.get("run_id"))
        print("data_interval_start =", context.get("data_interval_start"))
        print("data_interval_end =", context.get("data_interval_end"))

    show_context()

backfill_experiment()
```

First trigger manually and inspect the run type.

Then use the Airflow 3.x backfill command available in your installed
version. Verify exact CLI syntax with:

``` bash
docker compose exec airflow airflow backfill --help
```

Create historical runs for:

``` text
2026-09-08
2026-09-09
2026-09-10
```

The original Airflow 3.3.1 experiment created three independent backfill
runs.

### Important evidence correction

The original experiment observed backfill context where the logged
start/end values equaled each logical timestamp. That runtime evidence
contradicted an earlier expectation about full-day interval boundaries.

The lesson is more important than the specific representation:

> **Runtime evidence beats our assumption about framework semantics.**

## Missing contract

Our processing scripts still process the entire dataset.

So:

``` text
Airflow backfill capability
       ≠
business-correct historical processing
```

A future contract should look like:

``` bash
python build_daily_revenue.py --business-date 2026-09-09
```

and publish:

``` text
/lake/curated/daily_revenue/date=2026-09-09/revenue.parquet
```

## Questions

1.  What is the difference between retry and backfill?
2.  What is the difference between manual and scheduled runs?
3.  Why must processing receive logical scope explicitly?
4.  Why should orchestration, processing, and storage recovery
    boundaries align?

## Principle

> Scheduling, Retry, and Backfill are orchestration capabilities;
> correctness depends on the processing contract.

------------------------------------------------------------------------

# Session 29 --- Failure, State & Observability in Airflow

## Goal

Diagnose a permanent failure from the smallest useful execution
boundary.

## DAG

`airflow/dags/observability_experiment.py` (**Reconstructed Lab Code
closely matching recorded behavior**):

``` python
from datetime import datetime, timedelta
from pathlib import Path

from airflow.sdk import dag, task

@dag(
    dag_id="observability_experiment",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
)
def observability_experiment():

    @task(
        retries=2,
        retry_delay=timedelta(seconds=5),
    )
    def extract_data(**context):
        run_id = context.get("run_id")
        ti = context.get("ti")
        try_number = getattr(ti, "try_number", None)

        print("=== EXTRACT DATA ===")
        print("Run ID:", run_id)
        print("Try number:", try_number)

        path = Path("/lake/raw/ilostat/input.csv")

        if not path.exists():
            raise FileNotFoundError(
                "/lake/raw/ilostat/input.csv does not exist"
            )

    @task
    def transform_data():
        print("TRANSFORM")

    @task
    def publish_data():
        print("PUBLISH")

    extract = extract_data()
    transform = transform_data()
    publish = publish_data()

    extract >> transform >> publish

observability_experiment()
```

## Prediction --- answer before running

1.  With `retries=2`, how many total attempts are possible?
2.  If the file never appears, what is the final state of
    `extract_data`?
3.  Will `transform_data` execute?
4.  Will `publish_data` execute?
5.  Where should you inspect first?

## Run

Ensure this file does **not** exist:

``` text
/lake/raw/ilostat/input.csv
```

Trigger:

``` bash
docker compose exec airflow \
  airflow dags trigger observability_experiment
```

Inspect the UI:

``` text
DAG Run
  ↓
extract_data
  ↓
attempts
  ↓
logs
```

## Original runtime evidence --- 2026-10-03

``` text
DAG Run       = FAILED
extract_data  = FAILED, Try 3
transform     = UPSTREAM FAILED, Try 0
publish       = UPSTREAM FAILED, Try 0
```

Recorded final log evidence included:

``` text
Run ID: manual__2026-10-03T05:25:57.953760+00:00
Try number: 3
FileNotFoundError:
/lake/raw/ilostat/input.csv does not exist
```

## Mental model

``` text
Something is wrong
   ↓
State
   ↓
Failure location
   ↓
Attempts
   ↓
Logs
   ↓
Evidence
   ↓
Root cause
```

## Failure semantics

**FAILED** --- the task actually executed and failed.

**UPSTREAM FAILED** --- the task did not execute because a required
predecessor failed.

## Questions

1.  Did retry repair the missing file?
2.  Why is this a permanent rather than transient failure under current
    conditions?
3.  Is three identical failures proof that every future attempt would
    fail?
4.  What evidence localizes the problem without reading all pipeline
    logs?
5.  Why is retry history itself diagnostic evidence?

## Principles

> Retry is a recovery mechanism, not a repair mechanism.

> Observability reduces the search space between symptom and cause.

------------------------------------------------------------------------

# Session 30 --- Final Architecture Review

## Goal

Decide what has actually been validated and close the Playground without
pretending it is production-ready.

## Evidence matrix

  Capability                  Runtime evidence
  --------------------------- -----------------------------------------
  Container reproducibility   Dockerized services and jobs
  Persistence                 PostgreSQL named volume
  Idempotent ingestion        rerun kept five rows
  Bulk loading                COPY benchmark and atomic failure
  Columnar storage            Parquet size/query experiments
  Partitioning                non/month/day benchmarks
  Pushdown/skipping           metadata + physical ordering experiment
  Data Lake                   Raw → Cleaned → Curated
  Distributed model           Spark partitions/tasks/stages
  Shuffle                     groupBy physical plan
  Recovery                    intentional Spark task retry
  DAG dependency              Airflow cleaned → curated
  Scheduling                  scheduler-created run
  Retry                       controlled transient failure
  Backfill                    historical Airflow runs
  Failure propagation         FAILED → UPSTREAM FAILED
  Observability               DAG → Task → Attempt → Log

## Airflow decision

For the **Big Data Playground**, Airflow was accepted because the
experiments demonstrated the required orchestration concepts.

This became:

``` text
ADR-003 — Use Apache Airflow for Workflow Orchestration
Status: Accepted for Playground
```

It is **not automatically accepted for ILOSTAT**.

## Spark decision boundary

Spark was learned and validated as a distributed-processing model.

It is **not automatically selected for ILOSTAT**.

## Final architecture challenge

A developer says:

> "We have one million records. This is Big Data. Let's use Spark +
> Airflow + Data Lake now so we don't need to change later."

Do not answer with a technology preference.

Ask:

1.  Why is this called Big Data?
2.  Which actual problem requires Spark?
3.  Which coordination problem requires Airflow?
4.  Which storage/consumer problem requires a Data Lake?
5.  What benefit does each technology provide over not using it?
6.  What operational cost does each add?
7.  Is there a simpler option?
8.  What evidence would prove the decision?

## Principle

> Architecture is not choosing impressive technologies. Architecture is
> knowing why a capability is needed, what it costs, and what evidence
> supports the decision.

------------------------------------------------------------------------

# FINAL COURSE REVIEW

# A. The Complete Mental Model

The whole course can be compressed into one reasoning chain:

``` text
Business Problem
      ↓
Requirements
      ↓
Quality Attributes
      ↓
Workload
      ↓
Data representation
      ↓
Reduce unnecessary work
      ↓
Measure
      ↓
Meet requirement?
 ┌────┴────┐
Yes        No
 │          ↓
Stop     Optimize / Scale Up
             ↓
         Still insufficient?
          ┌──┴──┐
         No    Yes
          │      ↓
        Stop   Scale Out?
                 ↓
          Coordination complex?
             ┌──┴──┐
            No    Yes
             │      ↓
           Simple  Orchestrator?
                   ↓
            Experiment / Evidence
                   ↓
                Decision
```

The important point is that **technology appears late**.

------------------------------------------------------------------------

# B. Storage Review

## CSV

Strengths:

-   simple;
-   portable;
-   human-readable;
-   low setup cost.

Weaknesses for analytics:

-   text parsing;
-   weak typing;
-   often scans unnecessary columns;
-   little structural metadata for skipping.

## Parquet

Provides:

-   columnar representation;
-   schema;
-   compression;
-   row-group metadata;
-   opportunities for column pruning and data skipping.

But:

> Parquet is not "always faster."

Small workloads may be dominated by fixed overhead.

## Partitioning

Storage partitioning creates a file/directory-level pruning opportunity.

Example:

``` text
orders/
├── order_month=2026-01/
├── order_month=2026-02/
└── ...
```

A query for August can avoid unrelated months if the engine understands
the partition predicate.

But too many partitions can produce:

-   many files;
-   metadata overhead;
-   filesystem/object-store operations;
-   scheduler overhead downstream.

## Three layers of avoiding work

``` text
Partition Pruning
      ↓
Candidate Parquet files
      ↓
Row-group Data Skipping
      ↓
Candidate row groups
      ↓
Column Pruning
      ↓
Required columns
```

Then predicate evaluation handles remaining rows.

------------------------------------------------------------------------

# C. Data Lake Review

The Playground model:

``` text
Raw
 ↓
Cleaned
 ↓
Curated
 ↓
Data Product
```

## Raw

Responsibility:

> Preserve source truth sufficiently for future reprocessing/audit.

Raw is not automatically "bad data." It is data closest to the source
contract.

## Cleaned

Responsibilities:

-   validate;
-   normalize;
-   type;
-   enforce basic data contracts.

## Curated

Responsibilities:

-   business aggregation;
-   consumer-oriented structure;
-   useful analytical meaning.

## Important distinction

``` text
Curated ≠ automatically Data Warehouse
Data Lake ≠ automatically Lakehouse
```

Do not introduce Lakehouse table formats until concrete needs such as
transactional table behavior, schema evolution, concurrency, or
governance justify them.

------------------------------------------------------------------------

# D. Distributed Processing Review

## Storage partition vs processing partition

``` text
Storage partition
→ What can be skipped?

Processing partition
→ What can run independently/in parallel?
```

## Spark execution

``` text
Application
  ↓
Job
  ↓
Stage
  ↓
Task
```

Driver coordinates. Executors execute tasks.

## Narrow dependency

Child partition can be computed from a limited parent partition set.

Typical examples:

-   map;
-   filter.

## Wide dependency

Data from many parent partitions must be redistributed.

Typical example:

-   groupBy key.

This creates shuffle and usually a stage boundary.

## Recovery

``` text
Failed Task
   ↓
Lineage
   ↓
Recompute required partition/work
```

The architecture value is not "Spark retries." It is:

> Failure can be recovered at a smaller boundary than the whole job.

------------------------------------------------------------------------

# E. Scaling Review

## Scale Up

Give one machine more:

-   CPU;
-   memory;
-   faster disk;
-   faster network.

Advantages:

-   simpler;
-   less coordination;
-   fewer distributed failure modes.

Limit:

-   finite machine size/cost.

## Scale Out

Add workers/machines.

Advantages:

-   parallel capacity;
-   potential horizontal growth.

Costs:

-   coordination;
-   network/shuffle;
-   skew;
-   distributed state;
-   partial failure;
-   observability;
-   operations.

## Decision

``` text
Do not scale because data “sounds large.”
Scale because measured requirements are not met.
```

------------------------------------------------------------------------

# F. Orchestration Review

## Processor vs orchestrator

``` text
Processor:
How is data transformed?

Orchestrator:
Which job runs?
When?
After what?
What state is it in?
Should it retry?
Which historical scope is being processed?
```

## DAG

A DAG makes execution dependency machine-readable.

An edge means:

``` text
B depends on A
```

It does **not** mean every task must be sequential.

The absence of a dependency can expose parallelism.

## Critical path

Optimizing work outside the critical path may not improve end-to-end
completion time.

## Retry

Retry repeats a failed execution unit.

It is appropriate when failure may be transient.

## Backfill

Backfill creates executions for historical logical scopes.

It is not the same as retry.

## Business correctness

``` text
Airflow can retry
≠
pipeline is safely retryable

Airflow can backfill
≠
processing is backfill-correct
```

These require application-level execution contracts.

------------------------------------------------------------------------

# G. Observability Review

## Evidence hierarchy

``` text
System
 ↓
Pipeline / DAG Run
 ↓
Task
 ↓
Attempt
 ↓
Operation
 ↓
Log / Metric / Data Evidence
 ↓
Cause
```

Start broad enough to identify the failed boundary, then progressively
narrow.

## Symptom vs cause

Example:

``` text
Evidence:
duration increased from 10m to 25m

Observed problem:
performance degradation

Potential impact:
future SLA violation

Possible root causes:
- pruning stopped working
- source volume increased
- skew increased
- dependency latency increased
- resource contention
```

Do not label the symptom as the root cause merely because it is the
first thing visible.

------------------------------------------------------------------------

# H. Architecture Decision Framework

Use this sequence for future systems:

``` text
Problem
 ↓
Requirements
 ↓
Hard Constraints
 ↓
Quality Attributes
 ↓
Options
 ↓
Trade-offs
 ↓
Technology Hypothesis
 ↓
Small Experiment / PoC
 ↓
Evidence
 ↓
Decision
 ↓
ADR
```

## Architecture decision worksheet

``` markdown
# Decision

## Context
What problem exists?

## Evidence
How do we know?

## Quality Attributes
Which measurable/important properties are affected?

## Constraints
What cannot be changed?

## Options
What realistic alternatives exist?

## Trade-offs
What does each option improve and cost?

## Experiment
What is the smallest test that could change our mind?

## Result
What did runtime evidence show?

## Decision
What do we choose, for this context?

## Revisit when
Which future condition invalidates the decision?
```

------------------------------------------------------------------------

# I. Production Gap Map

The Playground is deliberately **not production-ready**.

  Area            Playground            Deferred production depth
  --------------- --------------------- ---------------------------------
  Storage         Local filesystem      object/distributed storage
  Parquet         basic schema          schema evolution/compatibility
  Data Lake       Raw/Cleaned/Curated   catalog/governance/lineage
  Publishing      direct output         atomic/transactional publish
  Processing      Python/local Spark    cluster deployment/tuning
  Partitioning    controlled workload   evolving production workload
  Airflow         standalone            production topology/HA/upgrades
  Security        minimal               secrets/AuthN/AuthZ/encryption
  Observability   state/attempt/log     metrics/alerting/tracing/SLO
  Recovery        retry/backfill        DR/HA/recovery objectives
  Data Quality    validation            continuous quality monitoring
  Operations      Docker local          production CI/CD/operations

These are:

> **Deferred complexity, not forgotten architecture.**

## Date-aware processing --- identified, not implemented

Future contract:

``` text
Airflow Run Scope
      =
Processing Business Date
      =
Storage Partition
```

Example:

``` text
run:     2026-09-09
process: 2026-09-09
publish: date=2026-09-09
```

## Atomic publish --- identified, not implemented

Desired pattern:

``` text
write temporary
    ↓
validate
    ↓
valid?
 ┌──┴──┐
No    Yes
│       ↓
keep   atomic publish
old
valid
output
```

------------------------------------------------------------------------

# J. Transition to ILOSTAT Career Data Platform

The Playground was:

``` text
Learning-driven
Concept → Experiment → Evidence → Mental Model
```

ILOSTAT should be:

``` text
Problem-driven
Real Problem
   ↓
Stakeholder Decision
   ↓
Evidence Needed
   ↓
Can the data support it?
   ↓
Smallest useful indicator
   ↓
Vertical slice
   ↓
Measure usefulness
   ↓
Next architecture problem
```

The first vertical slice should remain small:

``` text
One real ILOSTAT source
  ↓
Raw
  ↓
Cleaned
  ↓
Vietnam
  ↓
One occupation dimension
  ↓
One useful indicator
  ↓
One query/API
  ↓
One visualization
  ↓
One useful career insight
```

Do **not** automatically carry these technologies forward:

-   PostgreSQL
-   Parquet
-   Spark
-   Airflow
-   Data Lake

Carry forward instead:

-   mental models;
-   experiments;
-   evidence discipline;
-   trade-off reasoning;
-   architecture vocabulary;
-   decision framework.

------------------------------------------------------------------------

# K. Architecture Vocabulary Map

## Containers & Runtime

**Image** --- packaged template used to create containers.\
**Container** --- isolated running instance of an image.\
**Build Context** --- files available to a Docker build.\
**Volume** --- storage with a lifecycle independent of a container.\
**Health Check** --- evidence that a service is ready/healthy according
to a defined probe.

## Ingestion

**Idempotency** --- safe re-execution without unintended duplicate
effect.\
**Bulk Load** --- ingest many records as one high-throughput operation.\
**Atomicity** --- operation behaves as an indivisible success/failure
boundary.\
**Staging** --- intermediate area used before trusted/final processing.

## Analytical Storage

**Columnar Storage** --- organize values by column for analytical
access.\
**Row Group** --- Parquet block with independent metadata/statistics.\
**Column Pruning** --- read only required columns.\
**Predicate Pushdown** --- move filtering closer to the storage reader.\
**Data Skipping** --- avoid blocks proven irrelevant by metadata.\
**Partition Pruning** --- avoid physical partitions that cannot match.\
**Small Files Problem** --- overhead created by too many small physical
files/partitions.

## Data Lake

**Raw** --- source-truth-oriented zone.\
**Cleaned** --- validated and normalized zone.\
**Curated** --- business-ready analytical zone.\
**Data Contract** --- explicit expectations data must satisfy.\
**Data Product** --- data prepared to serve a consumer/use case.\
**Reprocessability** --- ability to regenerate derived data from
retained inputs.

## Distributed Processing

**Processing Partition** --- independently processable work/data slice.\
**Task** --- computation for a processing partition within a stage.\
**Driver** --- Spark coordinator.\
**Executor** --- Spark task execution process.\
**Shuffle** --- redistribution so related data can meet.\
**Stage** --- group of tasks separated from another group by shuffle
boundary.\
**Lineage** --- transformation history enabling recomputation.\
**Skew** --- uneven distribution of data/work.\
**Straggler** --- slow task that determines completion time.

## Scaling

**Scale Up** --- increase resources of one machine.\
**Scale Out** --- add workers/machines.\
**SLA** --- required service/performance target.\
**Amdahl's Law** --- serial work limits speedup from parallelism.

## Orchestration

**DAG** --- directed acyclic graph of workflow dependencies.\
**Critical Path** --- dependency path determining earliest completion.\
**Scheduling** --- deciding when runs are created.\
**Retry** --- another attempt of failed execution.\
**Backfill** --- historical logical executions.\
**Task Instance** --- one task definition in one particular run.\
**Failure Propagation** --- upstream failure affecting downstream
eligibility.\
**Failure Localization** --- finding the smallest relevant failed
boundary.\
**Control Plane** --- coordinates execution/state.\
**Data Plane** --- performs actual data work.

## Architecture

**Quality Attribute** --- property such as performance, reliability,
security, operability, maintainability.\
**Baseline** --- measured starting point.\
**Trade-off** --- benefit paid for by cost/weakness elsewhere.\
**Technology Hypothesis** --- testable belief that a technology solves
the identified problem.\
**Decision Context** --- constraints/requirements under which a decision
is valid.\
**Deferred Complexity** --- known complexity postponed until a
requirement justifies it.

------------------------------------------------------------------------

# L. Final Self-review Questions

Do not look for model answers. Explain these in your own words.

1.  Why is a Docker container not the right place to permanently own
    database state?
2.  Why does `depends_on` not automatically mean a dependency is ready?
3.  Why did COPY outperform row INSERT, and what failure trade-off
    appeared?
4.  Why can CSV outperform Parquet on a small workload?
5.  Explain partition pruning, data skipping, and column pruning as
    three different boundaries.
6.  Why did daily partitioning win one query but lose badly on yearly
    access?
7.  Why did sorting by `amount` help one predicate and hurt another?
8.  Why should Raw survive even after Cleaned exists?
9.  What exact evidence would justify Spark?
10. Explain Storage Partition vs Processing Partition.
11. Why does `groupBy` create shuffle?
12. Why can Spark retry one task instead of restarting everything?
13. What is the difference between Scale Up and Scale Out?
14. Why is a DAG more than a list of tasks?
15. What is the difference between topological order and critical path?
16. Why does retry require idempotency?
17. Why is backfill a business-time problem, not merely a scheduler
    feature?
18. Why is SUCCESS insufficient evidence of system health?
19. What is the difference between FAILED and UPSTREAM FAILED?
20. Why is retry not a repair mechanism?
21. What is the difference between Airflow's Control Plane and
    processing's Data Plane?
22. Why does "Airflow supports backfill" not prove the pipeline is
    backfill-correct?
23. Why is Airflow accepted for the Playground but not automatically for
    ILOSTAT?
24. Why is Spark knowledge still valuable if ILOSTAT never needs Spark?
25. Explain "No technology without a problem."
26. Explain "No decision without a trade-off."
27. Explain "No claim without evidence."
28. What is deferred complexity?
29. What should trigger revisiting an ADR?
30. If someone proposes Spark + Airflow + Data Lake because "this is Big
    Data," what questions should you ask before discussing
    implementation?

------------------------------------------------------------------------

# M. Course Completion Standard

A learner has not completed this course merely because every command
ran.

The intended outcome is demonstrated when the learner can look at a new
data-system problem and reason:

``` text
What problem?
What evidence?
Which Quality Attribute?
What is unnecessary work?
What is the simplest option?
What trade-off?
What experiment?
What did runtime evidence show?
What decision is justified now?
When should we revisit it?
```

That is the durable skill.

> **No technology without a problem.\
> No decision without a trade-off.\
> No claim without evidence.**
