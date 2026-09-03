# Architectural Vocabulary Map

## Week 0 · 7/08/2026
       Problem
       │
       ├── Variation
       │      └── Strategy
       │
       ├── Object creation
       │      └── Factory
       │
       ├── External system
       │      └── Adapter
       │
       ├── Dependency direction
       │      └── Dependency Inversion
       │
       ├── Complex domain
       │      └── DDD [Domain-Driven Design]
       │
       ├── Read / Write asymmetry
       │      └── CQRS [Command Query Responsibility Segregation]
       │
       ├── Independent deployment
       │      └── Microservices
       │
       └── Distributed communication
              └── Messaging / Event-driven


## Week 1 · 27/08/2026

       Problem
       │
       ├── Behavior varies by context
       │      └── Strategy
       │
       ├── Object creation varies
       │      └── Factory
       │
       ├── External / incompatible interface
       │      └── Adapter
       │
       ├── Dependency points toward implementation
       │      └── Dependency Inversion → [Business says WHAT; Infrastructure decides HOW].
       │
       ├── Infrastructure leaks into business logic
       │      └── Ports & Adapters / Hexagonal Architecture
       │
       ├── Different components own different lifecycles
       │      └── Ownership / Lifecycle Management
       │
       ├── Same concept implemented differently
       │      └── Architectural Drift
       │
       ├── Knowledge scattered across many places
       │      ├── Single Source of Truth
       │      └── Docs-as-Code
       │
       ├── Documentation diverges from implementation
       │      └── Documentation Drift
       │
       ├── Need to preserve reasoning behind decisions
       │      └── ADR [Architecture Decision Record] → [Git remembers WHAT; ADR remembers WHY].
       │
       ├── Need smallest end-to-end proof
       │      └── Walking Skeleton → [Smallest REAL end-to-end system].
       │
       ├── Complex domain
       │      └── DDD [Domain-Driven Design]
       │
       ├── Read / Write asymmetry
       │      └── CQRS [Command Query Responsibility Segregation]
       │
       ├── Independent deployment
       │      └── Microservices
       │
       └── Distributed communication
              └── Messaging / Event-driven

       Problem
       │
       ├── Need speed now at the cost of future work
       │      └── Technical Debt
       │          "Borrow development speed today and pay the cost later."
       │
       ├── Implementation gradually diverges from intended design
       │      └── Architectural Drift
       │          "The implementation slowly moves away from the intended architecture."
       │
       └── Technical compromises accumulate without being corrected
              └── Architectural Decay
              "Unpaid compromises gradually make the system harder to change."        

       Data Storage
       │
       ├── Analytical workload
       │      └── Columnar Storage
       │             └── Parquet
       │
       ├── Read fewer columns
       │      └── Column Pruning
       │
       ├── Read less data
       │      └── Data Skipping
       │
       ├── Organize data blocks
       │      └── Row Groups
       │
       ├── Understand data without parsing everything
       │      └── Schema + Metadata
       │
       └── Optimization worth using when?
              └── Crossover Point     

       Data Storage
       │
       ├── Transaction workload
       │      └── OLTP
       │
       ├── Large analytical storage
       │      └── Data Lake
       │
       ├── Separate processing from persistence
       │      └── Storage–Compute Decoupling
       │
       ├── Data lifecycle
       │      └── Data Zones
       │             ├── Raw
       │             ├── Cleaned
       │             └── Curated
       │
       ├── Rebuild data from source
       │      └── Reprocessability
       │
       └── Unmanaged lake
              └── Data Swamp
                  

       Data Layout
       │
       ├── File Format
       │      └── Parquet
       │
       └── Inside File
       │      ├── Row Groups
       │      ├── Data Skipping
       │      └── Column Pruning
       │       
       ├── Split dataset physically
       │      └── Partitioning
       │             │
       │             ├── Partition Key
       │             ├── Partition Granularity
       │             ├── Partition Cardinality
       │             ├── Partition Pruning
       │             ├── Partition Selectivity
       │             └── Hierarchical Partitioning
       │
       ├── Too many small files
       │      └── Small Files Problem
       │
       ├── Correct partition metadata
       │      └── Partition Invariant
       │
       └── Optimization trade-off
              └── Diminishing Returns

       Query Performance
       │
       ├── Avoid partitions
       │      └── Partition Pruning
       │
       ├── Avoid blocks
       │      └── Data Skipping
       │
       ├── Avoid columns
       │      └── Column Pruning
       │
       ├── Move filter toward storage
       │      └── Predicate Pushdown
       │
       ├── Describe blocks
       │      └── Row Group Statistics
       │
       ├── Arrange values physically
       │      └── Physical Ordering
       │
       └── Optimize progressively
              └── Layered Optimization

       Data Lake
       │
       ├── Source truth
       │      └── Raw Zone
       │
       ├── Trusted data
       │      └── Cleaned Zone
       │
       ├── Business-ready data
       │      └── Curated Zone
       │
       ├── Trust boundary
       │      └── Data Contract
       │
       ├── Rebuild from source
       │      └── Reprocessability
       │
       └── Safe visibility
              └── Atomic Publish  


       Big Data Storage & Processing
       │
       ├── Efficient analytical format
       │      └── Parquet
       │
       ├── Avoid irrelevant files
       │      └── Partition Pruning
       │
       ├── Avoid irrelevant blocks
       │      └── Data Skipping
       │
       ├── Avoid irrelevant columns
       │      └── Column Pruning
       │
       ├── Push filtering toward storage
       │      └── Predicate Pushdown
       │
       ├── Organize values for workload
       │      └── Physical Ordering
       │
       ├── Separate storage from processing
       │      └── Storage–Compute Decoupling
       │
       ├── Manage data lifecycle
       │      └── Data Zones
       │
       ├── Protect trusted data
       │      └── Data Contract
       │
       ├── Rebuild derived data
       │      └── Reprocessability
       │
       └── Handle increasing workload
              ├── Scale Up
              └── Scale Out   


## Week 2 - 31/08/2026

       Scale Problem
       │
       ├── Unnecessary data
       │      ├── Partition Pruning
       │      ├── Data Skipping
       │      └── Column Pruning
       │
       ├── Filtering too late
       │      └── Predicate Pushdown
       │
       ├── Poor physical organization
       │      └── Physical Layout / Ordering
       │
       ├── Single-machine capacity
       │      └── Scale Up
       │
       └── Single-machine limit
              └── Scale Out                                     


       Distributed Processing
       │
       ├── Divide data
       │      └── Processing Partition
       │
       ├── Execute partition
       │      └── Task
       │
       ├── Run tasks
       │      └── Worker
       │
       ├── Run work simultaneously
       │      └── Parallelism
       │
       ├── Uneven work
       │      └── Data Skew
       │
       └── Partition granularity
              └── Parallelism ↔ Overhead trade-off


       Spark Application
       │
       ├── Coordinate execution
       │      └── Driver
       │
       ├── Execute work
       │      └── Executor
       │
       ├── Describe computation
       │      └── Transformation
       │
       ├── Demand result
       │      └── Action
       │
       ├── Delay execution
       │      └── Lazy Evaluation
       │
       └── Execution hierarchy
              └── Job
                     └── Stage
                            └── Task
                                   └── Partition    


       Distributed Aggregation
       │
       ├── Independent local work
       │      └── Partial Aggregation
       │
       ├── Related data must meet
       │      └── Shuffle
       │           └── Exchange
       │
       ├── Execution boundary
       │      └── Stage
       │
       ├── Combine related data
       │      └── Final Aggregation
       │
       └── Runtime optimization
              └── Adaptive Query Execution [AQE]
                     │
                     └── Coalesce small partitions       


       Distributed Processing
       │
       ├── Divide work
       │     └── Processing Partition
       │           └── Task
       │                 └── Worker / Executor
       │
       ├── Execute simultaneously
       │     └── Parallelism
       │
       ├── Uneven work
       │     └── Data Skew
       │           └── Straggler
       │
       ├── Cross-partition dependency
       │     └── Wide Dependency
       │           └── Shuffle
       │                 └── Stage
       │
       ├── Local dependency
       │     └── Narrow Dependency
       │
       ├── Reduce data movement
       │     └── Partial Aggregation
       │
       ├── Runtime optimization
       │     └── AQE
       │
       └── Failure recovery
              ├── Task Attempt
              ├── Retry
              └── Lineage                                                        