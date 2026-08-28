# ADR-002 — Partition Orders by Month

## Status

- Accepted

## Context

The analytical orders dataset supports primarily time-based
business queries:

- Daily revenue
- Monthly revenue
- Revenue comparison between months
- Occasional yearly revenue

Three physical data layouts were evaluated:

- Non-partitioned
- Partition by month
- Partition by day

The experiment used 1,000,000 orders distributed across 2026.

## Decision

Partition analytical order data by month using:

`order_month=YYYY-MM`

Example:

`order_month=2026-08/`

## Evidence

| Workload | Non-partitioned | By Month | By Day |
| --- | ---: | ---: | ---: |
| Daily | 0.030599s | 0.008411s | 0.004164s |
| Monthly | 0.043685s | 0.007643s | 0.054943s |
| Yearly | 0.026792s | 0.024896s | 0.571435s |

Layout creation:

- Non-partitioned: 0.236s
- Monthly: 0.591s
- Daily: 4.726s

## Rationale

Daily partitioning is optimized for daily queries but introduces
significant overhead for broader workloads.

Monthly partitioning provides good daily performance, the best
monthly performance in the experiment, and efficient yearly
performance while keeping partition cardinality moderate.

It therefore provides the best balance for the current business
workload.

## Alternatives Considered

### Non-partitioned

Advantages:
- Simplest layout
- Low write and file-management overhead

Disadvantages:
- Weaker daily and monthly query performance

### Daily partitioning

Advantages:
- Best daily query performance

Disadvantages:
- 365 partitions per year
- Higher layout creation cost
- Poor monthly and yearly performance in the experiment
- Greater risk of the Small Files Problem

## Consequences

Positive:

- Effective pruning for daily and monthly workloads
- Moderate partition cardinality
- Simple physical layout

Negative:

- Daily queries are not maximally optimized
- Queries spanning many months must read multiple partitions

## Revisit When

Re-evaluate this decision if:

- Business query patterns change significantly
- Data volume changes substantially
- Daily queries become the dominant workload
- File sizes become too small or too large
- Storage/query technology changes