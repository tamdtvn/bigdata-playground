# Session 08 --- First Data Pipeline: Command Reference

## Purpose

Quick command reference for **Sprint 2 --- Session 8**.

Pipeline:

``` text
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
```

The ingestion pipeline is designed to be **idempotent**: running it
again with the same input does not create duplicate orders.

------------------------------------------------------------------------

## 1. Start the Environment

Run from the `playground/` directory:

``` bash
docker compose up -d
```

Check service status:

``` bash
docker compose ps
```

Build images and start services:

``` bash
docker compose up --build
```

------------------------------------------------------------------------

## 2. Work with the Ingestion Container

Open a shell inside the running ingestion container:

``` bash
docker compose exec ingestion bash
```

Check the working directory:

``` bash
pwd
```

Inspect application files:

``` bash
ls -l /app
```

Inspect mounted datasets:

``` bash
ls -l /data
```

Read the input dataset:

``` bash
cat /data/orders.csv
```

Exit the container shell:

``` bash
exit
```

------------------------------------------------------------------------

## 3. Verify the Read-Only Dataset Mount

The dataset bind mount is configured as read-only:

``` yaml
volumes:
  - ../datasets:/data:ro
```

From inside the ingestion container, try to create a file:

``` bash
touch /data/test.txt
```

Expected result:

``` text
Read-only file system
```

This verifies that the ingestion service can read the source dataset but
cannot modify it.

------------------------------------------------------------------------

## 4. Inspect Docker Mounts

Run this command from the **host**, not from inside the container:

``` bash
docker inspect playground-ingestion-1 --format '{{json .Mounts}}'
```

For `/data`, look for:

``` text
"Destination":"/data"
"Mode":"ro"
"RW":false
```

If the Compose mount configuration was changed, recreate the ingestion
container:

``` bash
docker compose up -d --force-recreate ingestion
```

------------------------------------------------------------------------

## 5. PostgreSQL Database

Open PostgreSQL:

``` bash
docker compose exec postgres psql -U postgres
```

Create the Playground database if it does not already exist:

``` sql
CREATE DATABASE playground;
```

Exit `psql`:

``` text
\q
```

Connect directly to the Playground database:

``` bash
docker compose exec postgres psql -U postgres -d playground
```

List databases:

``` text
\l
```

Describe the `orders` table:

``` text
\d orders
```

------------------------------------------------------------------------

## 6. Run the Ingestion Pipeline

Run ingestion as a temporary container:

``` bash
docker compose run --rm ingestion
```

`--rm` removes the temporary ingestion container after it finishes.

Data flow:

``` text
orders.csv
    |
    v
ingest_orders.py
    |
    v
INSERT ... ON CONFLICT DO NOTHING
    |
    v
PostgreSQL orders table
```

------------------------------------------------------------------------

## 7. Verify Loaded Data

Connect to PostgreSQL:

``` bash
docker compose exec postgres psql -U postgres -d playground
```

Display all orders:

``` sql
SELECT * FROM orders ORDER BY order_id;
```

Count records:

``` sql
SELECT COUNT(*) FROM orders;
```

For the Session 8 dataset, the verified result was:

``` text
5 rows
```

------------------------------------------------------------------------

## 8. Verify Idempotency

Run ingestion again:

``` bash
docker compose run --rm ingestion
```

Then check:

``` sql
SELECT COUNT(*) FROM orders;
```

Expected:

``` text
Run #1 -> 5 rows
Run #2 -> 5 rows
```

The primary key plus:

``` sql
ON CONFLICT (order_id) DO NOTHING
```

prevents duplicate orders.

------------------------------------------------------------------------

## 9. Useful Logs and Troubleshooting

Show all Compose logs:

``` bash
docker compose logs
```

Show PostgreSQL logs:

``` bash
docker compose logs postgres
```

Show ingestion logs:

``` bash
docker compose logs ingestion
```

Show all containers, including stopped containers:

``` bash
docker compose ps -a
```

### PostgreSQL database does not exist

If ingestion reports:

``` text
FATAL: database "playground" does not exist
```

connect to PostgreSQL:

``` bash
docker compose exec postgres psql -U postgres
```

and create it:

``` sql
CREATE DATABASE playground;
```

A useful lesson from this session:

> `POSTGRES_DB` is used during first-time PostgreSQL initialization.
> Adding it later does not create the database inside an already
> initialized persistent volume.

------------------------------------------------------------------------

## 10. Key Commands at a Glance

``` bash
# Build and start
docker compose up --build

# Check services
docker compose ps

# Enter ingestion container
docker compose exec ingestion bash

# Inspect source data
cat /data/orders.csv

# Run ingestion
docker compose run --rm ingestion

# Connect to the Playground database
docker compose exec postgres psql -U postgres -d playground

# Inspect mounts
docker inspect playground-ingestion-1 --format '{{json .Mounts}}'

# PostgreSQL logs
docker compose logs postgres

# Stop/remove runtime containers and network, preserving named volumes
docker compose down
```

Useful PostgreSQL commands:

``` sql
SELECT * FROM orders ORDER BY order_id;
SELECT COUNT(*) FROM orders;
```

------------------------------------------------------------------------

## Key Reminders

-   `postgres:5432` is used for container-to-container communication
    through the Docker network.
-   `/data` is a **read-only bind mount** from the repository's
    `datasets/` directory.
-   Input data is not copied into the ingestion image; application and
    input-data lifecycles remain separate.
-   `docker compose run --rm ingestion` is useful for one-off ingestion
    jobs.
-   `ON CONFLICT (order_id) DO NOTHING` makes this ingestion safe to
    rerun for duplicate IDs.
-   Idempotency does **not** automatically mean source and destination
    are fully synchronized.
-   `docker compose down` preserves named volumes by default.
-   Avoid `docker compose down -v` when persistent data must be
    retained.

------------------------------------------------------------------------

## Session 8 Mental Model

``` text
Source                 Compute                 Storage
------                 -------                 -------

orders.csv  ------->   Python   ----------->  PostgreSQL
    |                  Ingestion                   |
    |                                              |
read-only                                      persistent
bind mount                                       volume
```

> A pipeline is not reliable because it succeeds once; it is reliable
> when it can safely succeed again.
