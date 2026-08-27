# Architectural Vocabulary Map

## Week 1 · 7/08/2026
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