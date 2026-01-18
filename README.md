# Semantic Dropdown Search

> A lightweight, MIT-licensed semantic indexing layer that replaces hashtags with structured, human-selected dropdown descriptors.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-orange.svg)](VERSION)

---

## Overview

Instead of tagging text with free-form keywords, content is described using **finite, versioned semantic fields** — domain, intent, tone, audience, stability, and more. This makes text easier to search, filter, and reason about for both humans and machines.

**This project is designed to be embedded, not centralized.**

---

## Why This Exists

### The Problem with Hashtags

Hashtags were a workaround. They are:

- **Ambiguous and overloaded** — `#design` could mean graphic design, game design, or system design
- **Easy to game** — spamming popular tags for visibility
- **Flat** — no hierarchy or relationships
- **Hostile to serious search** — finding what you actually want is difficult

### The Solution

Modern text discovery needs **structure without surveillance** and **meaning without manipulation**.

Semantic Dropdown Search provides:

- ✓ Constrained semantic choices
- ✓ Transparent intent signaling
- ✓ Machine-readable metadata
- ✓ Human-legible meaning

**No ranking tricks. No hidden models. No behavioral profiling.**

---

## Core Concept

Every text object is paired with a **semantic descriptor object** chosen from dropdown-style schemas.

### Instead of This:

```
#ai #science #health #research #thoughts
```

### You Get This:

```json
{
  "domain": "Science → Biology → Systems Biology",
  "intent": "Research → Conceptual → Early-stage",
  "tone": "Analytical / Cautious",
  "audience": "Researchers",
  "stability": "Hypothesis (Not yet validated)"
}
```

**Result:** Search becomes precise, explainable, and meaningful.

---

## What This Is (and Is Not)

### ✓ This Is:

- A semantic indexing layer
- A structured metadata schema
- A search and filter primitive
- Embeddable infrastructure

### ✗ This Is Not:

- A social network
- A recommender algorithm
- A crawler or scraper
- An AI prediction system

**The goal is clarity, not virality.**

---

## Design Principles

| Principle | Description |
|-----------|-------------|
| **Finite vocabularies** | All dropdowns are constrained and versioned |
| **Human-first semantics** | Descriptors are selected intentionally by authors |
| **Machine-readable by default** | Schemas are JSON-based and stable |
| **No training, no tuning** | No hidden models or personalization |
| **Platform-agnostic** | Works anywhere text exists |
| **MIT-licensed** | Free to embed, fork, and extend |

---

## Repository Structure

```
semantic-dropdown-search/
│
├── 📄 README.md              # Project overview, quick start, philosophy
├── 📄 LICENSE                # MIT license
├── 📄 CITATION.cff           # Academic / research citation metadata
├── 📄 CHANGELOG.md           # Release history and notable changes
├── 📄 VERSION                # Current package version (v1.0.0)
├── 📁 .github/               # GitHub metadata (funding, workflows, templates)
│
├── 📁 docs/                  # Conceptual and integration documentation
│   ├── 📁 modules/           # Module-level technical documentation
│   │   ├── core_module.md    # Core semantics, validation, normalization
│   │   ├── indexer_module.md # Indexing and persistence layer
│   │   ├── query_module.md   # Query engine and predicates
│   │   └── api_module.md     # API surface and contracts
│   ├── philosophy.md         # Design philosophy and guiding principles
│   ├── design_principles.md  # Non-negotiable architectural rules
│   ├── schema_versioning.md  # Schema lifecycle and compatibility rules
│   ├── integration_guide.md  # How to embed in real systems
│   └── faq.md                # Common questions and guarantees
│
├── 📁 schema/                # Semantic schema definitions
│   ├── v1/                   # Stable schema version v1
│   │   ├── domain.json       # Content domain taxonomy
│   │   ├── intent.json       # Content intent taxonomy
│   │   ├── tone.json         # Tone and communication style
│   │   ├── audience.json     # Intended audience classification
│   │   ├── stability.json    # Maturity / confidence signaling
│   │   └── README.md         # Schema usage and conventions
│   └── registry.json         # Schema version registry and metadata
│
├── 📁 core/                  # Semantic foundations
│   ├── __init__.py
│   ├── validate.py           # Schema validation engine
│   ├── normalize.py          # Canonical normalization logic
│   ├── descriptor.py         # SemanticDescriptor data model
│   └── errors.py             # Core exception hierarchy
│
├── 📁 indexer/               # Text indexing and storage
│   ├── __init__.py
│   ├── index_text.py         # IndexedText + TextIndex implementations
│   ├── serialize.py          # JSON / NDJSON / CSV serialization
│   └── adapters.py           # Storage adapters (file, memory, directory)
│
├── 📁 query/                 # Query engine
│   ├── __init__.py
│   ├── query_builder.py      # Fluent query construction API
│   ├── filters.py            # High-level filter helpers
│   ├── predicates.py         # Predicate primitives and logic
│   └── explain.py            # Human-readable query explanations
│
├── 📁 api/                   # External API definitions
│   ├── openapi.yaml          # OpenAPI specification
│   └── 📁 examples/          # API request/response examples
│       ├── index_request.json
│       └── search_request.json
│
├── 📁 examples/              # End-to-end usage examples
│   ├── 📁 posts/             # Example content descriptors
│   │   ├── research_post.json
│   │   ├── blog_post.json
│   │   └── forum_post.json
│   ├── 📁 queries/           # Example query definitions
│   │   ├── cautious_research.json
│   │   └── early_stage_filter.json
│   └── end_to_end.md         # Full indexing → querying walkthrough
│
├── 📁 tests/                 # Test suite
│   ├── tests.md              # How to run and interpret tests
│   ├── __init__.py
│   ├── test_schema.py        # Schema validation tests
│   ├── test_validation.py   # Descriptor validation tests
│   ├── test_query.py        # Query engine tests
│   ├── run_tests.py         # Test runner
│   └── 📁 fixtures/
│        └── sample_descriptors.json
│
└── 📁 tools/                 # Maintenance and migration utilities
    ├── schema_linter.py      # Schema validation and consistency checks
    └── migration_helper.py   # Schema migration and compatibility tooling

```

> **Note:** You can adopt only the schema, or the schema plus helpers — whatever fits your needs.

---

## Example: Precision Search

### Query:

> Show me:
> - Conceptual biology posts
> - Written cautiously
> - Intended for researchers
> - Explicitly marked as unvalidated

### Why This Matters:

**This is impossible to do reliably with hashtags.**

With Semantic Dropdown Search, this query maps directly to structured fields, returning exactly what you're looking for.

---

## Use Cases

Semantic Dropdown Search is ideal for:

- 🔬 **Research platforms** — filtering by validation stage and audience
- 💻 **Developer forums** — distinguishing questions from solutions
- ✍️ **Long-form blogging tools** — organizing by tone and intent
- 📚 **Knowledge bases** — structuring internal documentation
- 🌐 **Open-source projects** — clarifying contribution types
- 🗣️ **Social platforms** — enabling non-manipulative discovery

---

## Philosophy

Semantic Dropdown Search treats text as **intentional communication**, not engagement bait.

### Authors Are Encouraged to State:

- **What they are doing** — research, documentation, opinion
- **Who it is for** — experts, learners, general audience
- **How stable the content is** — hypothesis, validated, canonical

### Readers Are Empowered to Search Based On:

**Meaning, not popularity.**

---

## Getting Started

### 1. Explore the Schema

Start by reviewing the semantic fields in `schema/v1/`:

```bash
ls schema/v1/
# domain.json  intent.json  tone.json  audience.json  stability.json
```

### 2. Tag Your Content

Describe your text using the dropdown options:

```python
from core.descriptor import SemanticDescriptor

descriptor = SemanticDescriptor(
    domain="Science → Biology → Systems Biology",
    intent="Research → Conceptual → Early-stage",
    tone="Analytical / Cautious",
    audience="Researchers",
    stability="Hypothesis (Not yet validated)"
)
```

### 3. Index and Search

```python
from indexer.index_text import index
from query.query_builder import QueryBuilder

# Index your content
index(text="Your content here", descriptor=descriptor)

# Build precise queries
query = QueryBuilder()
    .filter_domain("Science → Biology")
    .filter_stability("Hypothesis")
    .filter_tone("Cautious")
    .build()
```

See `examples/end_to_end.md` for complete workflows.

---

## Contributing

Contributions are welcome! Whether it's:

- Schema improvements
- Bug fixes
- Documentation enhancements
- Use case examples

Please open an issue or pull request.

---

## License

**MIT License** — use it, ship it, improve it.

See [LICENSE](LICENSE) for full details.

---

## Author

**Don Michael Feeney Jr.**

This project is part of a broader effort to improve epistemic clarity, safety, and trust in technical communication.

---

## Citation

If you use this project in your research or product, please cite:

```bibtex
@software{semantic_dropdown_search,
  author = {Feeney, Don Michael Jr.},
  title = {Semantic Dropdown Search},
  year = {2026},
  url = {https://github.com/dfeen87/semantic-dropdown-search}
}
```

See [CITATION.cff](CITATION.cff) for more formats.

---

## Links

- 📖 [Documentation](docs/)
- 🔧 [API Reference](api/openapi.yaml)
- 💡 [Examples](examples/)
- ❓ [FAQ](docs/faq.md)
- 📝 [Changelog](CHANGELOG.md)

---

<div align="center">

**Built for clarity. Designed to be embedded.**

</div>
