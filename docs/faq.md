# Frequently Asked Questions (FAQ)

This FAQ answers common questions about **Semantic Dropdown Search**, its design,
scope, and intended usage.

---

## What problem does Semantic Dropdown Search solve?

Semantic Dropdown Search replaces **free-form tags, hashtags, and ambiguous filters**
with **structured, validated semantic descriptors**.

It solves problems such as:
- inconsistent tagging,
- meaningless keyword matches,
- unclear search intent,
- unexplainable filtering behavior,
- and schema drift over time.

---

## Is this a search engine?

No.

Semantic Dropdown Search is **not** a full-text search engine and does not attempt to
replace tools like Elasticsearch, PostgreSQL full-text search, or vector databases.

It is a **semantic governance layer** that:
- structures meaning,
- validates intent,
- and enables explainable filtering.

It pairs naturally with traditional search systems.

---

## Why use dropdowns instead of free text?

Free text introduces ambiguity and inconsistency.

Dropdowns:
- enforce controlled vocabularies,
- prevent invalid combinations,
- ensure compatibility across time,
- and make meaning explicit.

Dropdowns are not a UI limitation — they are a **semantic contract**.

---

## Can users still type text?

Yes.

Text content remains free-form.  
Only the **semantic descriptor** is structured.

Users describe *what they wrote* using dropdowns, not *how they write*.

---

## Is machine learning required?

No.

The system is:
- deterministic,
- rule-based,
- and fully explainable.

No embeddings, no training, no probability thresholds.

This makes it suitable for:
- regulated domains,
- academic systems,
- moderation pipelines,
- and governance-heavy platforms.

---

## Does this work with AI systems?

Yes.

Semantic Dropdown Search is **AI-friendly by design**.

It provides:
- clean semantic inputs,
- stable labels,
- explainable metadata.

AI systems benefit from **structured intent**, not raw text alone.

---

## What happens if a schema changes?

Schemas are **versioned and immutable**.

- Existing data remains valid forever.
- New schema versions do not overwrite old ones.
- Migration is explicit and opt-in.

Schema versioning rules are documented in `schema_versioning.md`.

---

## Is this tied to a specific frontend or backend?

No.

The system is:
- frontend-agnostic,
- backend-agnostic,
- framework-agnostic.

It works with:
- REST APIs,
- GraphQL,
- file-based systems,
- in-memory indexes,
- databases.

---

## Is this suitable for production?

Yes.

Version **v1.0.0** is considered:
- API-stable,
- schema-stable,
- behavior-stable.

Breaking changes will only occur in future **major** releases.

---

## How strict is validation?

Validation is configurable.

You can:
- validate fully,
- validate partially,
- or disable validation at load time.

However, strict validation is **strongly recommended** for production systems.

---

## What happens if validation fails?

Validation failures:
- do not crash the system,
- return structured error messages,
- and can be handled programmatically.

You can choose to:
- reject content,
- flag content,
- or allow partial descriptors.

---

## Can I add custom fields?

Yes.

Descriptors support **custom fields** in addition to standard schema fields.

Custom fields:
- are normalized,
- stored,
- and queryable,
- but not schema-validated by default.

This allows gradual extension without schema forks.

---

## Can I localize schemas?

Yes.

Schemas are JSON-based and can be localized or translated.

However:
- canonical values must remain stable,
- localization should occur at the UI layer.

---

## Is this a taxonomy system?

Partially.

Semantic Dropdown Search supports:
- hierarchies,
- parent/child relationships,
- depth constraints.

However, it does not attempt to model full ontologies or inference systems.

---

## How is this different from tags?

Tags are:
- unvalidated,
- ambiguous,
- user-defined,
- inconsistent.

Semantic descriptors are:
- validated,
- controlled,
- explainable,
- and versioned.

This is the core difference.

---

## Does this replace moderation systems?

No — but it helps them.

Structured semantics:
- improve moderation clarity,
- enable policy-aware filtering,
- and reduce ambiguity in decisions.

---

## What kinds of platforms use this?

Typical use cases include:
- research repositories,
- forums,
- documentation portals,
- governance systems,
- knowledge bases,
- content platforms.

---

## Is this overkill for small projects?

Not necessarily.

The system scales down:
- minimal schemas,
- partial validation,
- simple queries.

It scales up:
- complex hierarchies,
- strict governance,
- explainable filtering.

---

## What is the long-term vision?

The long-term goal is **semantic stability**.

Meaning should:
- outlive UI redesigns,
- survive platform migrations,
- remain interpretable years later.

Semantic Dropdown Search treats meaning as infrastructure.

---

## Where do I start?

Recommended path:
1. Review `philosophy.md`
2. Read `integration_guide.md`
3. Explore `examples/`
4. Use schema v1

---

## Support and Contributions

This project is open-source.

Contributions should:
- respect schema stability,
- preserve backward compatibility,
- prioritize clarity over cleverness.

---

## Status

**FAQ Version:** v1.0.0  
**Project Status:** Stable  
**Schema Compatibility:** v1  

---

If meaning matters, structure it.
