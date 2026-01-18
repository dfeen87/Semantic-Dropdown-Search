# Changelog

All notable changes to this project will be documented in this file.

This project follows semantic versioning.

---

## [1.0.0] — 2026-01-18

### Initial Stable Release

This is the first stable release of **Semantic Dropdown Search**.

The project provides a complete, schema-driven system for
semantic classification, indexing, and querying of text content
using validated dropdown-based descriptors.

---

### Core Features

#### Schema System
- Versioned semantic schemas (`schema/v1`)
- Hierarchical value support
- Explicit required field enforcement
- Central schema registry

#### Core Engine
- Canonical normalization of semantic values
- Deterministic validation with human-readable errors
- Strongly typed `SemanticDescriptor` object
- Strict separation of normalization vs validation

#### Indexing
- Text + descriptor pairing
- Content deduplication via hashing
- Metadata support
- In-memory indexing with pluggable storage adapters
- JSON, NDJSON, and CSV serialization

#### Query System
- Predicate-based query engine
- Hierarchical matching (exact or descendant)
- Fluent query builder API
- High-level filters for common patterns
- Explainable queries and results

#### Tooling
- Schema linter for validating schema correctness
- Migration helper for future schema upgrades
- Storage adapters (file, directory, memory)

---

### Documentation & Examples
- Architecture and philosophy documentation
- Design principles and schema versioning strategy
- Integration guide for applications and APIs
- End-to-end usage examples
- Sample posts and queries

---

### Stability Guarantees
- All schemas under `v1` are immutable
- Query semantics are deterministic
- No breaking changes within major version 1

---

### Intended Audience
- Search and discovery systems
- Knowledge management tools
- Research platforms
- Content moderation and governance pipelines
- Any system requiring **stable meaning over time**

---

### What’s Next
- Optional storage backends (SQL, vector DB adapters)
- UI reference components
- Performance benchmarks
- Additional schema versions (v2+)

---

Initial release. No deprecations.
