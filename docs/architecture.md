## Infrastructure Foundation

- The Big Data Playground uses Docker as the foundation for isolated, reproducible environments.
- Multiple services communicate through Docker networks.
- Services should communicate using service names rather than hard-coded container IP addresses.
- Docker Compose is used to define and orchestrate the local multi-container environment.

                 Docker
                    │
       ┌────────────┼────────────┐
       │            │            │
     Image      Container      Network
       │            │            │
       │       Dockerfile        │
       │            │            │
       └────────────┼────────────┘
                    │
               Compose
                    │
                    ▼
          Multi-container System

### Persistent Storage

Stateful services use Docker volumes for persistent data.

PostgreSQL data is stored in the `postgres_data` volume rather than being coupled directly to the PostgreSQL container lifecycle.   

### Pipeline Reliability

PostgreSQL exposes a Healthcheck using `pg_isready`.

The ingestion job waits for PostgreSQL to become healthy before starting.

The ingestion application also retries transient database connection
failures using Exponential Backoff.

This provides two layers of protection:

- Infrastructure readiness: Healthcheck
- Application resilience: Retry + Backoff

                    Big Data Playground

 datasets/orders.csv
        │
        │ read-only bind mount
        ▼
┌───────────────────────┐
│ Python Ingestion Job  │
│                       │
│ Retry + Backoff       │
└──────────┬────────────┘
           │
           │ postgres:5432
           ▼
┌───────────────────────┐
│ PostgreSQL            │
│                       │
│ Healthcheck           │
└──────────┬────────────┘
           │
           ▼
    postgres-data
       Volume


### Ingestion Performance Review

Two ingestion strategies were evaluated using 100,000 records.

| Strategy          |        Row-by-row INSERT |          PostgreSQL COPY |
| ----------------- | -----------------------: | -----------------------: |
| Row-by-row INSERT | 8.08s                    | 12,369 rows/sec          |
| PostgreSQL COPY   | 0.10s                    | 988,933 rows/sec         |



| Tiêu chí          |        Row-by-row INSERT |          PostgreSQL COPY |
| ----------------- | -----------------------: | -----------------------: |
| 100k rows         |                    8.08s |                    0.10s |
| Throughput        |            12,369 rows/s |           988,933 rows/s |
| Performance       |                 Thấp hơn |             ~80x cao hơn |
| Failure isolation |                  Tốt hơn |                  Thô hơn |
| Atomicity         | Tùy transaction strategy |                   Rất rõ |
| Bad row           |    Có thể xử lý từng row | Có thể fail cả bulk load |
| Complexity        |                 Đơn giản |         Cao hơn một chút |


PostgreSQL COPY provided approximately 80x higher throughput in this
experiment.

However, an intentional invalid record caused the COPY operation to fail
and the transaction to roll back completely.

No ingestion strategy has been selected as the final architecture yet.

Future design should consider:

- Performance
- Data Quality
- Failure Granularity
- Atomicity
- Maintainability
- Observability       
