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

## Columnar Storage
→ "Đặt dữ liệu cùng column gần nhau để analytics đọc hiệu quả."

## Column Pruning
→ "Không cần column nào thì đừng đọc column đó."

## Data Skipping
→ "Biết block không chứa thứ cần tìm thì bỏ qua cả block."

## Row Group
→ "Chia Parquet thành các khối để có thể xử lý và skip theo khối."

## Schema
→ "File tự biết dữ liệu của nó có cấu trúc và kiểu gì."

## Metadata
→ "Thông tin về dữ liệu giúp engine quyết định trước khi đọc dữ liệu."

## Crossover Point
→ "Điểm mà lợi ích của optimization bắt đầu lớn hơn chi phí của nó."

## Partitioning
Physically organizes a dataset into subsets based on partition keys.
→ "Chia dataset theo cách business thường truy cập."

## Partition Key
The field used to determine which partition contains data.
→ "Column dùng để quyết định data nằm ở partition nào."

## Partition Granularity
How finely a dataset is divided into partitions.
→ "Chia data thô hay mịn đến mức nào."

## Partition Cardinality
The number of distinct partitions produced by a partition strategy.
→ "Partition key tạo ra bao nhiêu partitions."

## Partition Pruning
Skipping partitions that cannot satisfy a query predicate.
→ "Query bỏ cả partition không cần đọc."

## Partition Selectivity
How effectively a query predicate eliminates unnecessary partitions.
→ "Query loại bỏ được bao nhiêu partitions."

## Small Files Problem
Performance and operational overhead caused by splitting data into
too many small files.
→ "Quá nhiều file nhỏ khiến overhead lớn hơn lợi ích chia nhỏ."

## Partition Invariant
The requirement that data physically stored in a partition must actually satisfy that partition's value.
→ "Partition nói data thuộc đâu thì data bên trong phải thực sự thuộc đó."

## Diminishing Returns
The point where additional optimization cost produces progressively smaller benefits.
→ "Tốn thêm rất nhiều nhưng chỉ nhận thêm một ít." [Hiệu suất giảm dần]

## Partition Pruning
→ "Không cần partition thì đừng mở."

## Data Skipping
Avoiding physical data blocks that cannot satisfy a query predicate.
→ "Không cần block thì đừng đọc."

## Column Pruning
→ "Không cần column thì đừng đọc."

## Predicate Pushdown
Moves filtering conditions closer to the data reader so unnecessary data can potentially be avoided.
→ "Lọc càng gần data càng tốt."

## Layered Optimization
Reducing unnecessary work progressively across multiple data-access layers.
→ "Mỗi tầng cùng loại bỏ một phần công việc không cần thiết."

## Predicate Pushdown
→ "Đưa filter xuống gần data."

## Row Group Statistics
Metadata such as min/max values describing data inside a Parquet row group.
→ "Metadata giúp biết block có khả năng chứa kết quả không."

## Physical Ordering
Organizing related values close together physically so metadata can better eliminate unnecessary data.
→ “Đặt những giá trị liên quan gần nhau để metadata có thể giúp engine bỏ data không cần đọc.”

## Data Lake
Storage for large volumes of data in multiple formats, decoupled from processing engines.

## Data Zone
A storage boundary representing a stage in the data lifecycle.

## Data Contract
Rules data must satisfy before consumers can trust it.

## Reprocessability
Ability to rebuild derived data from preserved source data.

## Data Product
A dataset designed for a clear consumer or business need.

## Atomic Publish
Expose new output to consumers only after processing and validation succeed.

## Scale Up
Increase the capacity of a single machine.

## Scale Out
Increase processing capacity by distributing work across multiple machines.

## SLA
A measurable service requirement, such as completing a daily processing
job within 30 minutes.

## Distributed Processing
Splitting data and computation across multiple workers to process a workload together.

## Processing Partition
A portion of a dataset that can be processed independently.

## Task
A unit of computation that processes one partition.

## Worker
A compute resource that executes tasks.

## Parallelism
The amount of work that can execute simultaneously.

## Data Skew
Uneven distribution of data or work that causes some tasks to take significantly longer than others.

## Driver
The process that coordinates a Spark application and plans execution.

## Executor
A process that executes tasks and processes data for a Spark application.

## Transformation
An operation that describes a new computation without necessarily
executing it immediately.

## Action
An operation that requires Spark to execute computation and produce
a result.

## Lazy Evaluation
Delaying execution so Spark can understand and optimize a chain of
operations before running it.

## Physical Plan
Spark's selected execution strategy for performing a computation.

## Column Pruning
Reading only the columns required by a query.