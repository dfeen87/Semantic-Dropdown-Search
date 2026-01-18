# End-to-End Example

This document demonstrates a full lifecycle workflow using
Semantic Dropdown Search.

---

## 1. Authoring Content

A user writes content freely:

> “We explore a deterministic framework for semantic classification…”

They then select semantic descriptors using dropdowns.

---

## 2. Validation

The descriptor is validated against schema version `v1`.

- Invalid values are rejected
- Hierarchy is enforced
- Missing required fields are detected

---

## 3. Indexing

The content and descriptor are stored together:

- text content remains unstructured
- semantics are structured, validated, and normalized
- content is deduplicated via hash

---

## 4. Querying

A query is constructed:

- domain: Science
- intent: Research
- stability: Hypothesis

Hierarchical matches are included by default.

---

## 5. Explanation

Results are returned **with explanation**:

- why items matched
- why others did not
- how filters were applied

---

## 6. Long-Term Stability

Months or years later:

- schemas remain valid
- meaning is preserved
- queries behave identically

This is the core promise of Semantic Dropdown Search.

---

## Summary

Semantic Dropdown Search ensures that meaning is:
- explicit,
- stable,
- explainable,
- and future-proof.

Structure meaning once.
Query it forever.
