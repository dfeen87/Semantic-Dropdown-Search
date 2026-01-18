# Integration Guide

This guide explains how to integrate **Semantic Dropdown Search** into applications, platforms, APIs, and content systems.

The system is designed to be:
- framework-agnostic,
- storage-agnostic,
- UI-agnostic,
- and backward-compatible.

---

## Integration Philosophy

Semantic Dropdown Search replaces **unstructured tags and hashtags** with **structured, validated semantic descriptors**.

Instead of guessing meaning from free text, systems explicitly declare:

- what content is about,
- why it exists,
- who it is for,
- how stable or mature it is.

This enables:
- precise filtering,
- explainable search,
- deterministic behavior,
- and long-term semantic stability.

---

## Core Integration Flow

A typical integration follows four steps:

1. **Define schema version**
2. **Attach descriptors to content**
3. **Index content**
4. **Query using semantic filters**

Each step is explicit and controlled.

---

## 1. Schema Selection

All integrations must select a schema version.

Example:

```python
schema_version = "v1"
```

Schema versions are immutable and independent of software versions.

Schema metadata is available in:

```
schema/registry.json
```

## 2. Creating Semantic Descriptors

Descriptors describe content using structured fields.

Example:

```python
from core import SemanticDescriptor

descriptor = SemanticDescriptor(
    domain="Science → Biology",
    intent="Research → Conceptual",
    tone="Analytical",
    audience="Researchers",
    stability="Hypothesis"
)
```

Descriptors:

- normalize automatically,
- validate against schema rules,
- reject invalid values deterministically.

## 3. Validating Descriptors

Validation can be:

- partial (only provided fields),
- complete (all required fields).

Example:

```python
result = descriptor.validate(schema_version="v1")

if not result:
    print(result.errors)
```

For strict enforcement:

```python
descriptor.validate_or_raise(schema_version="v1")
```

## 4. Indexing Content

Content is indexed alongside its semantic descriptor.

Example:

```python
from indexer import TextIndex

index = TextIndex(schema_version="v1")

index.add(
    text="This paper explores early-stage biological systems...",
    descriptor=descriptor,
    metadata={"author": "A. Smith", "type": "paper"}
)
```

The index:

- deduplicates content by hash,
- enforces schema correctness,
- supports in-memory or persistent storage.

## 5. Persistence Options

Storage adapters allow flexible persistence.

Supported adapters:

- in-memory,
- single-file (JSON, NDJSON, CSV),
- directory-based storage.

Example:

```python
from indexer.adapters import FileAdapter, IndexManager

adapter = FileAdapter("data/index.ndjson")
manager = IndexManager(adapter)

manager.add(text, descriptor)
```

## 6. Querying Content

Queries are built using semantic predicates instead of keywords.

Example:

```python
from query import QueryBuilder

results = (
    QueryBuilder()
    .from_index(index)
    .where_domain("Science → Biology")
    .where_intent("Research", exact=False)
    .order_by_created()
    .limit(10)
    .execute()
)
```

Queries are:

- composable,
- explainable,
- deterministic.

## 7. Explainability

Every query can be explained in human-readable form.

Example:

```python
print(results.query_explanation)
```

You can also explain why a specific item matched or didn't match.

This is critical for:

- trust,
- moderation,
- audits,
- and user-facing explanations.

## 8. UI Integration (Dropdowns)

Semantic Dropdown Search is UI-agnostic.

Typical UI pattern:

- load schema JSON,
- render dropdowns from schema values,
- emit descriptor JSON.

Example UI payload:

```json
{
  "domain": "Science → Biology",
  "intent": "Research → Conceptual",
  "tone": "Analytical",
  "audience": "Researchers",
  "stability": "Hypothesis"
}
```

This payload maps directly to `SemanticDescriptor.from_dict()`.

## 9. API Integration

The system is API-friendly by design.

Descriptors are JSON-native.

Indexing and search map cleanly to REST or GraphQL.

OpenAPI examples are provided in `api/openapi.yaml`.

Typical API operations:

- `POST /index`
- `POST /search`
- `GET /schema`

## 10. Backward Compatibility

Key guarantees:

- Schema v1 descriptors will always remain valid.
- New schema versions never invalidate old data.
- Migration is explicit, never automatic.

This ensures long-term data safety.

## 11. Common Integration Patterns

Supported use cases include:

- forums and discussion platforms,
- research repositories,
- documentation portals,
- knowledge bases,
- moderation and governance systems.

The system scales from single-user tools to large platforms.

## 12. What This Is Not

Semantic Dropdown Search is not:

- a full-text search engine replacement,
- a machine-learning classifier,
- a probabilistic tagging system.

It is a semantic governance layer.

---

## Integration Checklist

Before production use:

- [ ] Schema version selected
- [ ] Descriptors validated
- [ ] Index persistence configured
- [ ] Queries tested
- [ ] Explainability verified

---

## Status

- **Integration Guide Version:** v1.0.0
- **Schema Compatibility:** v1
- **Stability:** Stable

---

## Next Steps

- See `examples/` for end-to-end usage
- See `docs/modules/` for internal architecture
- See `api/` for HTTP-based integration

---

**Semantic meaning is a contract.**  
**This system makes that contract explicit.**
```
