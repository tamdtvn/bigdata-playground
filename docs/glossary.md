# Glossary

## Data Lake
- A storage system that stores raw and processed data in its native format.

## Environment Drift
- Differences between development environments that can cause inconsistent behavior.

## Reproducible Environment
- An environment that can be recreated consistently across machines.

## Docker Image
A packaged artifact used to create containers.

## Container
A running instance of a Docker image.

## Immutable
An object that is not modified after it has been created.

## Port Publishing

Mapping a host port to a container port so that a service inside
a container can be accessed from outside its Docker network.

## System Boundary

The boundary that separates internal system components from
external clients or environments.

## Attack Surface

The set of externally reachable points that could potentially
be accessed or attacked.

## Data Ingestion

The process of moving data from a source into a destination system.

## Batch Processing

Processing data as groups of records rather than one record at a time.

## Bulk Load

Loading a large amount of data into a system efficiently.

## Idempotency

A property where repeating the same operation produces the same final state.

## Upsert

An operation that inserts a new record or handles an existing record
according to a defined conflict strategy.

## Bind Mount

A runtime mapping between a host file or directory and a container path.

## Least Privilege

Giving a component only the permissions it actually needs.

## Readiness

Whether a service is actually ready to accept and process requests.

## Healthcheck

A mechanism used to determine the health/readiness of a service.

## Transient Failure

A temporary failure that may succeed if the operation is retried later.

## Permanent Failure

A failure that retrying the same operation is unlikely to resolve.

## Retry

Repeating an operation after a recoverable failure.

## Exponential Backoff

A retry strategy where the waiting time increases between attempts.

Example:

1s → 2s → 4s → 8s

## Resilience

The ability of a system to handle failures and recover appropriately.

## One-off Job

A workload that performs a finite task and exits after completion.

## Quality Attribute

A measurable characteristic describing how well a system behaves,
such as Performance, Reliability, Security, or Maintainability.

## Quality Attribute Scenario

A concrete scenario used to make a Quality Attribute measurable
and testable.

## Baseline

A measured reference point used to evaluate future changes.

## Throughput

The amount of work processed per unit of time.

Example: rows / second

## Architectural Trade-off

A decision where improving one system quality may affect other qualities.

## Bulk Load

Loading a large amount of data efficiently as a bulk operation.

## Failure Granularity

The amount of work or data affected by a single failure.

## Atomicity

An operation either completes entirely or has no committed effect.

## Staging Area

An intermediate area where incoming data can be loaded, validated,
cleaned, or transformed before reaching its final destination.