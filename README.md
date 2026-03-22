# Semantic Dropdown Search

> A lightweight, non-commercially licensed semantic indexing layer that replaces hashtags with structured, human-selected dropdown descriptors.

[![Version](https://img.shields.io/badge/version-1.0.0-orange.svg)](VERSION)
[![CI](https://github.com/dfeen87/Semantic-Dropdown-Search/workflows/CI/badge.svg)](https://github.com/dfeen87/Semantic-Dropdown-Search/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

---

## Table of Contents

- [Overview](#overview)
- [Why This Exists](#why-this-exists)
- [Core Concept](#core-concept)
- [What This Is (and Is Not)](#what-this-is-and-is-not)
- [Design Principles](#design-principles)
- [Repository Structure](#repository-structure)
- [Example: Precision Search](#example-precision-search)
- [Use Cases](#use-cases)
- [Philosophy](#philosophy)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [API Quick Reference](#api-quick-reference)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [Acknowledgements](#acknowledgements)
- [License](#license)
- [Citation](#citation)

---

## Quick Start

**Get up and running in 60 seconds:**

```python
# 1. Clone and navigate
git clone https://github.com/dfeen87/Semantic-Dropdown-Search.git
cd Semantic-Dropdown-Search

# 2. Run tests to verify
python -m unittest discover tests

# 3. Try it out
python3 << 'EOF'
import sys
sys.path.insert(0, '.')

from core.descriptor import SemanticDescriptor
from indexer.index_text import TextIndex, IndexedText
from query.query_builder import QueryBuilder

# Create a descriptor
desc = SemanticDescriptor(
    domain="Science → Biology",
    intent="Research → Conceptual",
    tone="Analytical / Cautious",
    audience="Researchers",
    stability="Hypothesis (Not yet validated)"
)

# Index some content
index = TextIndex()
item = IndexedText(
    text="Exploring semantic classification frameworks",
    descriptor=desc
)
index.add(item)

# Query it
query = QueryBuilder().filter_domain("Science").build()
results = index.search(query)
print(f"Found {len(results)} results matching 'Science'")
EOF
```

**That's it!** You now have a working semantic search system.

---

## Project Status

| Aspect | Status |
|--------|--------|
| **Current Version** | v1.0.0 (Stable) |
| **Schema Stability** | ✅ v1 schemas are immutable |
| **API Stability** | ✅ Stable, semantic versioning |
| **Production Ready** | ✅ Yes |
| **Breaking Changes** | ⚠️ Only in major versions |
| **Python Support** | 3.9, 3.10, 3.11, 3.12 |
| **Dependencies** | Zero (core functionality) |

---

## Overview

Instead of tagging text with free-form keywords, content is described using **finite, versioned semantic fields** — domain, intent, tone, audience, stability, and more. This makes text easier to search, filter, and reason about for both humans and machines.

**This project is designed to be embedded, not centralized.**

### Key Features

- 🎯 **Precision Search** - Find exactly what you need using structured semantic filters
- 🔒 **Zero Dependencies** - Core functionality requires only Python 3.9+
- 📊 **Explainable Results** - Every query result comes with clear explanations
- 🔄 **Immutable Schemas** - v1 schemas guaranteed stable forever
- 🚫 **No Black Boxes** - Fully deterministic, no ML required
- 🏗️ **Hierarchical** - First-class support for semantic hierarchies
- 🔌 **Embeddable** - Integrate into any system, any platform
- 📝 **Open Source** - Non-commercial license, fork-friendly for non-commercial use

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

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Your Application Layer                        │
│          (Social Network, Forum, CMS, Knowledge Base)            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   Semantic Dropdown Search    │
         │     (This Framework)          │
         └───────┬───────────────────────┘
                 │
        ┌────────┼────────┬───────────────┐
        ▼        ▼        ▼               ▼
   ┌────────┐┌──────┐┌────────┐   ┌──────────┐
   │ Schema ││ Core ││Indexer │   │  Query   │
   │  v1    ││Valid.││Storage │   │ Engine   │
   └────────┘└──────┘└────────┘   └──────────┘
        │         │        │              │
        └─────────┴────────┴──────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │  Structured      │
              │  Semantic Data   │
              └──────────────────┘
```

### Data Flow

1. **Author** creates content and selects semantic descriptors from dropdowns
2. **Validation** ensures descriptors match schema (domain, intent, tone, etc.)
3. **Normalization** converts values to canonical form
4. **Indexing** stores text + semantics together
5. **Querying** filters content by semantic criteria
6. **Results** returned with explanations of why they matched

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

## Semantic Dropdown Search vs. Alternatives

| Feature | Semantic Dropdown Search | Hashtags | Full-Text Search | Vector Embeddings |
|---------|-------------------------|----------|------------------|-------------------|
| **Structure** | ✅ Structured dropdowns | ❌ Unstructured text | ❌ Free-form | ⚠️ Learned vectors |
| **Validation** | ✅ Schema-enforced | ❌ No validation | ❌ No validation | ❌ No validation |
| **Explainability** | ✅ Fully explainable | ❌ Ambiguous | ⚠️ Keyword matching | ❌ Black box |
| **Consistency** | ✅ Guaranteed | ❌ User-dependent | ⚠️ Limited | ⚠️ Model-dependent |
| **Versioning** | ✅ Immutable schemas | ❌ None | ❌ None | ⚠️ Model versions |
| **Hierarchy** | ✅ First-class | ❌ Flat | ❌ Flat | ⚠️ Implicit |
| **Precision** | ✅ Exact matches | ❌ Low | ⚠️ Moderate | ⚠️ Approximate |
| **ML Required** | ✅ No | ✅ No | ✅ No | ❌ Yes |
| **Stability** | ✅ Deterministic | ⚠️ Changes over time | ✅ Stable | ⚠️ Model drift |
| **Setup Complexity** | ⚠️ Schema design | ✅ Simple | ✅ Simple | ❌ Complex |

> **Note:** Semantic Dropdown Search is designed to **complement** full-text search and embeddings, not replace them. Use all three together for optimal results.

---

## Design Principles

| Principle | Description |
|-----------|-------------|
| **Finite vocabularies** | All dropdowns are constrained and versioned |
| **Human-first semantics** | Descriptors are selected intentionally by authors |
| **Machine-readable by default** | Schemas are JSON-based and stable |
| **No training, no tuning** | No hidden models or personalization |
| **Platform-agnostic** | Works anywhere text exists |
| **Non-commercially licensed** | Free to embed, fork, and extend for non-commercial use |

---

## Repository Structure

```
semantic-dropdown-search/
│
├── 📄 README.md              # Project overview, quick start, philosophy
├── 📄 LICENSE                
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

## Installation

### Prerequisites

- Python 3.9 or higher
- No external dependencies required for core functionality

### Basic Setup

1. **Clone the repository:**

```bash
git clone https://github.com/dfeen87/Semantic-Dropdown-Search.git
cd Semantic-Dropdown-Search
```

2. **Verify installation:**

```bash
python -m unittest discover tests
```

3. **Import and use:**

```python
# Add the project to your Python path or install locally
import sys
sys.path.append('/path/to/Semantic-Dropdown-Search')

from core.descriptor import SemanticDescriptor
from indexer.index_text import TextIndex
from query.query_builder import QueryBuilder
```

### Integration Options

You can integrate Semantic Dropdown Search into your project in several ways:

- **Direct inclusion**: Copy the `core/`, `indexer/`, `query/`, and `schema/` directories
- **Submodule**: Add as a git submodule: `git submodule add https://github.com/dfeen87/Semantic-Dropdown-Search.git`
- **Vendor**: Vendor the required modules into your project

> **Note:** This is a library/framework, not a standalone application. It's designed to be embedded into your existing systems.

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

## API Quick Reference

### Core Components

```python
# Create a semantic descriptor
from core.descriptor import SemanticDescriptor

descriptor = SemanticDescriptor(
    domain="Science → Biology → Systems Biology",
    intent="Research → Conceptual → Early-stage",
    tone="Analytical / Cautious",
    audience="Researchers",
    stability="Hypothesis (Not yet validated)"
)

# Validate against schema
from core.validate import validate_descriptor
is_valid, errors = validate_descriptor(descriptor, schema_version="v1")

# Normalize descriptor values
from core.normalize import normalize_descriptor
normalized = normalize_descriptor(descriptor)
```

### Indexing

```python
from indexer.index_text import TextIndex, IndexedText

# Create an index
index = TextIndex()

# Add content with semantics
indexed_item = IndexedText(
    text="Your content here",
    descriptor=descriptor,
    metadata={"author": "John Doe", "timestamp": "2026-02-14"}
)
index.add(indexed_item)

# Persist to disk
from indexer.serialize import serialize_to_file
serialize_to_file(index, "my_index.json")
```

### Querying

```python
from query.query_builder import QueryBuilder
from query.predicates import domain_matches, stability_equals

# Build structured queries
query = (QueryBuilder()
    .where(domain_matches("Science → Biology"))
    .where(stability_equals("Hypothesis"))
    .build())

# Execute query
results = index.search(query)

# Get explanations
from query.explain import explain_query
explanation = explain_query(query)
print(explanation)  # Human-readable query description
```

### Available Schema Fields (v1)

| Field | Description | Example Values |
|-------|-------------|----------------|
| `domain` | Content subject area | `Science → Biology`, `Engineering → Software` |
| `intent` | Purpose of content | `Research → Conceptual`, `Documentation → Tutorial` |
| `tone` | Communication style | `Analytical / Cautious`, `Casual / Conversational` |
| `audience` | Target readers | `Researchers`, `General Public`, `Experts` |
| `stability` | Content maturity | `Hypothesis`, `Validated`, `Canonical` |

See `schema/v1/` for complete hierarchies and valid values.

---

## Documentation

### Core Documentation

- 📖 [**Philosophy**](docs/philosophy.md) - Design rationale and principles
- 🏗️ [**Design Principles**](docs/design_principles.md) - Architectural decisions
- 📝 [**Integration Guide**](docs/integration_guide.md) - How to embed in your system
- ❓ [**FAQ**](docs/faq.md) - Frequently asked questions
- 🔄 [**Schema Versioning**](docs/schema_versioning.md) - Schema lifecycle and compatibility

### Module Documentation

- [Core Module](docs/modules/core_module.md) - Validation, normalization, descriptors
- [Indexer Module](docs/modules/indexer_module.md) - Storage and persistence
- [Query Module](docs/modules/query_module.md) - Query building and filtering
- [API Module](docs/modules/api_module.md) - API contracts and OpenAPI spec

### Examples

- 💡 [End-to-End Workflow](examples/end_to_end.md) - Complete usage example
- 📋 [Example Posts](examples/posts/) - Sample semantic descriptors
- 🔍 [Example Queries](examples/queries/) - Sample query patterns

---

## Contributing

We welcome contributions! Here's how to get involved:

### Ways to Contribute

- 🐛 **Bug Reports** - Found an issue? [Open a bug report](https://github.com/dfeen87/Semantic-Dropdown-Search/issues/new)
- 💡 **Feature Requests** - Have an idea? [Suggest a feature](https://github.com/dfeen87/Semantic-Dropdown-Search/issues/new)
- 📖 **Documentation** - Improve guides, fix typos, add examples
- 🧪 **Tests** - Add test coverage, improve test quality
- 🔧 **Code** - Fix bugs, implement features
- 🌐 **Schema Extensions** - Propose new semantic fields (with strong justification)

### Development Guidelines

1. **Respect schema stability** - v1 schemas are immutable
2. **Maintain backward compatibility** - Don't break existing APIs
3. **Prioritize clarity over cleverness** - Code should be readable
4. **Add tests for new functionality** - Maintain test coverage
5. **Update documentation** - Keep docs in sync with code
6. **Follow existing patterns** - Match the project's style

### Running Tests

```bash
# Run all tests
python -m unittest discover tests

# Run specific test module
python tests/test_schema.py

# Run with verbose output
python -m unittest discover tests -v
```

### Contribution Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests to ensure nothing breaks
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to your branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code of Conduct

- Be respectful and constructive
- Focus on what is best for the project
- Show empathy towards other contributors

Please open an issue or pull request for any contributions.

---

## Acknowledgements

I would like to acknowledge **Microsoft Copilot**, **Anthropic Claude**, and **OpenAI ChatGPT** for their meaningful assistance in refining concepts, improving clarity, and strengthening the overall quality of this work.

---

## License

This project is available for **non‑commercial use only** under the terms of the included LICENSE file.  
Commercial use requires a separate paid license.

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

## Troubleshooting

### Common Issues

**Q: `ModuleNotFoundError` when importing**

```python
# Solution: Add project to Python path
import sys
sys.path.insert(0, '/path/to/Semantic-Dropdown-Search')
```

**Q: Validation fails with "Invalid schema value"**

- Ensure your values exactly match those in `schema/v1/*.json`
- Check for typos and exact case/spacing
- Use `→` (not `->` or `-`) for hierarchy separators

**Q: Tests failing on import**

```bash
# Ensure you're in the project root directory
cd /path/to/Semantic-Dropdown-Search
python -m unittest discover tests
```

**Q: How do I add custom fields?**

Custom fields are supported! They're stored but not validated:

```python
descriptor = SemanticDescriptor(
    domain="Science",
    custom_field="my_value"  # This works!
)
```

**Q: Can I modify schema values?**

No. Schema v1 is immutable. However, you can:
- Propose additions in future major versions
- Create custom schemas for your own use
- Use custom fields for project-specific metadata

**Q: Performance issues with large indexes?**

- Use appropriate storage adapters (see `indexer/adapters.py`)
- Consider filtering early in your query pipeline
- Index incrementally rather than all at once

For more help, see [FAQ](docs/faq.md) or [open an issue](https://github.com/dfeen87/Semantic-Dropdown-Search/issues).

---

## Links

- 📖 [Documentation](docs/)
- 🔧 [API Reference](api/openapi.yaml)
- 💡 [Examples](examples/)
- ❓ [FAQ](docs/faq.md)
- 📝 [Changelog](CHANGELOG.md)
- 🐛 [Issues](https://github.com/dfeen87/Semantic-Dropdown-Search/issues)
- 🔀 [Pull Requests](https://github.com/dfeen87/Semantic-Dropdown-Search/pulls)

---

## Support

### Getting Help

- 📚 Start with the [FAQ](docs/faq.md) for common questions
- 📖 Read the [Integration Guide](docs/integration_guide.md) for implementation help
- 💬 Open a [GitHub Discussion](https://github.com/dfeen87/Semantic-Dropdown-Search/discussions) for questions
- 🐛 [Report bugs](https://github.com/dfeen87/Semantic-Dropdown-Search/issues/new) via GitHub Issues

### Community

- ⭐ Star this project if you find it useful
- 👁️ Watch for updates and releases
- 🍴 Fork to create your own variants
- 💖 [Sponsor](https://github.com/sponsors/dfeen87) to support development

---

## Roadmap

### Current Status (v1.0.0)

✅ Stable schema (v1)  
✅ Core validation and normalization  
✅ Indexing and persistence layer  
✅ Query engine with explanations  
✅ OpenAPI specification  
✅ Comprehensive documentation  

### Future Considerations

The following may be explored in future versions (no guarantees):

- Additional schema fields (with community input)
- Performance optimizations for large-scale indexing
- Additional storage adapters (databases, cloud storage)
- Language bindings (JavaScript, Go, Rust)
- Schema migration tooling enhancements
- GraphQL API specification
- Real-time indexing support

> **Note:** Any changes will respect semantic versioning and backward compatibility guarantees.

---

## Performance

### Design for Scale

Semantic Dropdown Search is designed to be **lightweight and efficient**:

- **Zero overhead schemas** - Validation is fast, using simple rule-based checks
- **Minimal memory footprint** - Only stores what you index
- **No ML inference costs** - Deterministic queries are instant
- **Lazy loading** - Schemas and indexes load on-demand
- **Serialization options** - JSON, NDJSON, CSV formats available

### Typical Performance

**Test Environment:** Standard developer laptop (Intel i5/Ryzen 5 class CPU, 16GB RAM, Python 3.10, Linux/macOS)

Approximate performance for typical workloads:

- **Schema validation:** ~10,000 descriptors/second (5-field descriptors, averaged)
- **Indexing:** ~5,000 items/second (in-memory, with 200-character text fields)
- **Query execution:** Sub-millisecond for typical predicates (simple domain/stability filters)
- **Serialization:** ~2,000 items/second to JSON (full descriptor objects)

> **Note:** These are approximate figures from informal testing. Actual performance depends on your hardware, storage adapter, query complexity, descriptor field count, text length, and system resources. For production deployments, benchmark with your actual data patterns.

### Scaling Strategies

For large-scale deployments:

1. **Use appropriate storage adapters** - Database-backed indexes scale better than in-memory
2. **Index incrementally** - Add items as they're created, not in bulk
3. **Partition by domain** - Separate indexes for different content domains
4. **Cache query results** - Common queries benefit from caching
5. **Combine with full-text search** - Use semantic filters to narrow results, then full-text within

### Benchmarking Your Implementation

```bash
# Run with timing
python -m timeit -n 1000 -s "from core.validate import validate_descriptor" "validate_descriptor(...)"

# Profile indexing
python -m cProfile -o profile.stats your_indexing_script.py
```

---

## Security

### Security Policy

This project follows responsible security practices:

- **No external dependencies** for core functionality reduces attack surface
- **Schema validation** prevents injection attacks via semantic fields
- **Deterministic behavior** - no hidden models or data exfiltration
- **Open source** - all code is auditable

### Reporting Security Issues

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT** open a public issue
2. **Preferred:** Use GitHub's [private vulnerability reporting](https://github.com/dfeen87/Semantic-Dropdown-Search/security/advisories/new)
3. **Alternative:** Email security concerns to the maintainer (see CITATION.cff for contact)
4. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and work with you to address the issue.

### Security Considerations for Implementers

When embedding Semantic Dropdown Search:

- ✅ **Do** validate all user inputs before descriptor creation
- ✅ **Do** sanitize text content before indexing
- ✅ **Do** implement access controls at your application layer
- ❌ **Don't** trust descriptors from untrusted sources without validation
- ❌ **Don't** expose raw file system paths via serialization adapters
- ❌ **Don't** store sensitive data in semantic descriptor fields

---

<div align="center">

**Built for clarity. Designed to be embedded.**

</div>
