# Changelog

All notable changes to this project will be documented in this file.

This project follows semantic versioning.

---

## [3.0.0] — 2026-10-03

### BEDROCK engineering baseline

This major release preserves the schema/core/indexer/query/API architecture
while making its validation and failure guarantees explicit.

- API ingestion now rejects missing or invalid descriptors instead of retrying
  with validation disabled, and batches commit atomically.
- Index updates and bulk loads validate candidate state before commit, keeping
  the prior index unchanged after rejection.
- Persistence rejects mismatched content hashes, invalid timestamps, duplicate
  IDs/content, and (by default) descriptors outside the selected schema.
- Embedding activation fails closed and configuration patches roll back when a
  requested model is unavailable.
- Similarity calculations reject NaN, infinity, malformed ranks, and dimension
  mismatches.
- CI now covers Python 3.9–3.12, schema linting, source compilation, and release
  version consistency in addition to the full test suite.

These stricter malformed-input and failure contracts are intentional Semantic
Versioning compatibility changes. See
[`docs/bedrock_v3.md`](docs/bedrock_v3.md) for migration details, regression
coverage, preserved architecture, and remaining deployment responsibilities.

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
