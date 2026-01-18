# Schema Versioning

This document describes how semantic schemas are versioned, validated,
and evolved in Semantic Dropdown Search.

Schema versioning is a core stability mechanism. It ensures that semantic
meaning remains consistent over time, even as the system evolves.

---

## 1. Purpose of Schema Versioning

Schemas define the **allowed semantic space** for descriptors.

Versioning exists to:
- preserve meaning,
- prevent silent semantic drift,
- enable safe evolution,
- and support backward compatibility.

A schema version is a contract between:
- content producers,
- indexing systems,
- query logic,
- and downstream consumers.

---

## 2. What Is a Schema Version?

A schema version represents a **fixed semantic definition set**.

Each version includes:
- a specific set of semantic fields,
- allowed values (including hierarchies),
- validation rules,
- and required/optional field definitions.

Once released, a schema version is immutable.

---

## 3. Directory Structure

Schemas are organized by version:

```
schema/
├── registry.json
└── v1/
    ├── domain.json
    ├── intent.json
    ├── tone.json
    ├── audience.json
    ├── stability.json
    └── README.md
```

Each version directory is self-contained.

---

## 4. Schema Registry

The `registry.json` file acts as the authoritative index of available
schema versions.

It defines:
- available versions,
- their status (active, deprecated),
- and human-readable metadata.

All schema resolution begins with the registry.

---

## 5. Version Naming Convention

Schema versions use simple, explicit identifiers:

- `v1`
- `v2`
- `v3`

Schema versions are **not** tied to software version numbers.

This allows:
- schema evolution independent of code releases,
- long-term support of older semantic definitions.

---

## 6. Backward Compatibility Rules

A schema version guarantees:

- identical validation behavior,
- identical interpretation of values,
- identical hierarchy semantics.

No breaking changes are allowed within a version.

Examples of **disallowed changes**:
- removing allowed values,
- changing hierarchy meaning,
- altering required fields,
- redefining semantics of existing labels.

---

## 7. Allowed Changes Within a Version

Within a schema version, only **non-semantic, non-breaking changes**
are allowed, such as:

- documentation clarifications,
- comments or formatting,
- tooling improvements that do not alter behavior.

If behavior changes, a new version is required.

---

## 8. When to Create a New Schema Version

A new schema version is required if any of the following occur:

- a semantic field is added or removed,
- allowed values are changed in meaning,
- hierarchy structure changes,
- validation rules change,
- required fields change.

If in doubt, create a new version.

---

## 9. Descriptor Validation and Version Selection

Every semantic descriptor is validated against a specific schema version.

Validation behavior:
- defaults to the latest active version,
- can be explicitly pinned by callers,
- produces deterministic results.

Descriptors are never auto-migrated silently.

---

## 10. Schema Migration Philosophy

Migration is **explicit**, not automatic.

When a new schema version is introduced:
- existing data remains valid under its original version,
- migration tools assist transformation,
- users decide when to migrate.

This avoids:
- unintended semantic reinterpretation,
- breaking historical data,
- and hidden data corruption.

---

## 11. Partial Validation

Partial validation allows:
- incomplete descriptors,
- progressive enrichment,
- early indexing workflows.

Partial validation:
- checks only present fields,
- respects schema constraints,
- does not enforce completeness.

Complete validation enforces all required fields.

---

## 12. Stability Guarantee for v1

Schema version `v1` is considered **stable**.

It represents:
- the baseline semantic model,
- long-term supported behavior,
- and reference semantics for the system.

Future schema versions may extend capabilities,
but `v1` will remain supported.

---

## 13. Design Intent

Schema versioning is intentionally conservative.

It prioritizes:
- trust over flexibility,
- clarity over convenience,
- and correctness over speed.

This ensures semantic integrity across time, systems, and users.

---

## Closing Note

Schemas define meaning.

Changing meaning requires intent, versioning, and transparency.
