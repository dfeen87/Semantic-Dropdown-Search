# Version 3.0.0 BEDROCK Engineering Baseline

Version 3.0.0 is a major release because it strengthens behavioral contracts at
validation, persistence, configuration, numerical, and API trust boundaries.
The established schema → core → indexer → query → API architecture remains in
place; the guarantees underneath it are now explicit and regression-tested.

This project follows Semantic Versioning. The Python method signatures remain
largely compatible, but the changes below intentionally reject inputs and
failure sequences that version 2 accepted. Applications relying on permissive
API ingestion or unvalidated persisted data must validate and repair that data
before upgrading.

## Explicit invariants

- Finalized descriptors entering the HTTP index contain every required schema
  field and every value belongs to the selected immutable schema version.
- A multi-field index update validates its complete candidate before mutation.
  Rejected updates preserve text, hash, descriptor, metadata, and timestamps.
- Bulk loading validates the entire candidate collection before commit. IDs and
  content hashes remain a consistent one-to-one index, including after errors.
- Serialized content hashes must authenticate the serialized text; timestamps
  must be timezone-aware and monotonic (`updated_at >= created_at`).
- HTTP batches are all-or-nothing and reject duplicate IDs within a request.
- Configuration changes that require an embedding model commit only after that
  dependency loads. Startup and runtime activation fail closed when it is
  unavailable.
- Cosine-similarity evidence must be finite, correctly ranked, and dimensionally
  compatible. NaN, infinity, and malformed matrices are rejected rather than
  influencing ranking.

## Changed failure behavior and compatibility

The previous API supplied descriptor defaults and retried failed validation with
validation disabled. Version 3 rejects missing or invalid required semantic
fields with HTTP 400, because untrusted data must not silently enter the
validated index. A failed embedding activation now returns HTTP 503 without
partially applying unrelated fields from the same configuration patch.
Deserialization now rejects forged/stale content hashes, naive or reversed
timestamps, duplicate bulk IDs/content, and invalid descriptors when
`validate_on_load=True`. These are behavioral-contract changes and justify the
major Semantic Versioning increment; they are not a redesign of public query or
schema concepts.

## Regression and CI enforcement

`tests/test_bedrock.py` proves update rollback, bulk-load rollback, persistence
integrity, timezone requirements, API batch atomicity, strict descriptor
validation, duplicate-ID rejection, configuration rollback, and finite,
shape-safe numerical evidence. CI runs the complete pytest suite and schema
linter on Python 3.9–3.12, compiles all runtime modules, and verifies that the
public source version and `VERSION` agree with 3.0.0.

## Intentionally preserved architecture

Schema v1 and its vocabulary are unchanged. Descriptor normalization, in-memory
indexing, predicate composition, deterministic query execution, serializers,
storage adapters, and optional embedding enhancement retain their existing
ownership boundaries. No new persistence service, ranking model, global state,
or abstraction layer was introduced.

## Remaining validation requirements

The in-memory API remains process-local and is not a transactional durable
store. Deployments requiring concurrency across workers, crash recovery,
authentication, authorization, rate limiting, or durable atomic commits must
provide and validate those controls at the hosting layer. Embedding quality,
model provenance, and suitability are external model/deployment concerns; the
tests establish software input and failure invariants, not ranking quality or
real-world certification. The SQLite configuration value remains reserved and
is not implemented by the current in-memory API backend.
