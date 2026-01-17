# Schema v1 - Semantic Fields

This directory contains the version 1 semantic field definitions for Semantic Dropdown Search.

## Overview

Each JSON file defines a semantic field with:
- A finite set of allowed values
- Hierarchical structure (where applicable)
- Required/optional status
- Field description

## Schema Files

### Core Fields

| Field | File | Required | Description |
|-------|------|----------|-------------|
| **domain** | `domain.json` | ✓ | Subject domain or field of content |
| **intent** | `intent.json` | ✓ | Purpose or intent of the content |
| **tone** | `tone.json` | | Tone or voice of the content |
| **audience** | `audience.json` | | Intended audience |
| **stability** | `stability.json` | | Validation status and stability |

## Schema Structure

Each schema file follows this format:

```json
{
  "version": "v1",
  "required": true,
  "description": "Human-readable description",
  "values": [
    "Simple Value",
    {
      "Parent": [
        "Child 1",
        "Child 2",
        {
          "Child 2": [
            "Grandchild 1",
            "Grandchild 2"
          ]
        }
      ]
    }
  ]
}
```

### Field Definitions

- **`version`** (string, required) - Schema version identifier (e.g., "v1")
- **`required`** (boolean, required) - Whether this field must be present in complete descriptors
- **`description`** (string, required) - Human-readable explanation of the field's purpose
- **`values`** (array, required) - List of valid values, including hierarchical structures

## Hierarchical Values

Values can be hierarchical, using the arrow separator `→`:

```
"Science → Biology → Systems Biology"
```

### Hierarchy Examples

**Domain:**
- `Science` (root)
- `Science → Biology` (parent → child)
- `Science → Biology → Systems Biology` (parent → child → grandchild)

**Intent:**
- `Research` (root)
- `Research → Conceptual` (parent → child)
- `Research → Conceptual → Early-stage` (parent → child → grandchild)

## Using Schemas

### Python

```python
from core import SemanticDescriptor, SchemaValidator

# Validate against v1 schemas
descriptor = SemanticDescriptor(
    domain="Science → Biology",
    intent="Research → Conceptual"
)

result = descriptor.validate(schema_version="v1")
```

### Direct Schema Access

```python
from core import SchemaValidator

validator = SchemaValidator(version="v1")

# Get valid values for a field
values = validator.get_valid_values("domain")

# Validate a specific field
result = validator.validate_field("domain", "Science → Biology")
```

## Schema Design Principles

### 1. Finite Vocabularies
All values are explicitly defined. No free-form text.

### 2. Human-Selected
Authors choose from predefined options, not algorithmic suggestions.

### 3. Hierarchical
Related values are grouped hierarchically for clarity.

### 4. Versioned
Schemas are versioned to allow evolution while maintaining compatibility.

### 5. Self-Documenting
Each schema includes descriptions and clear value names.

## Field Descriptions

### domain
**Purpose:** Classify the subject matter or field of knowledge.

**Examples:**
- `Science → Biology → Systems Biology`
- `Engineering → Software Engineering`
- `Philosophy`

**Use when:** You want to categorize content by academic or professional domain.

---

### intent
**Purpose:** Describe what the author is trying to accomplish.

**Examples:**
- `Research → Conceptual → Early-stage`
- `Documentation → Tutorial`
- `Opinion → Analysis`

**Use when:** You want to distinguish between questions, explanations, proposals, etc.

---

### tone
**Purpose:** Capture the voice or attitude of the content.

**Examples:**
- `Analytical / Cautious`
- `Technical / Accessible`
- `Exploratory`

**Use when:** The emotional or stylistic approach matters to readers.

---

### audience
**Purpose:** Indicate who the content is written for.

**Examples:**
- `Researchers`
- `Developers`
- `General Public`

**Use when:** You want to help readers find content at their level.

---

### stability
**Purpose:** Signal how validated or finalized the content is.

**Examples:**
- `Hypothesis (Not yet validated)`
- `Peer-reviewed`
- `Canonical`

**Use when:** Epistemic status matters (especially for research or evolving ideas).

## Extending Schemas

### Adding Values

To add new values to an existing field:

1. Edit the appropriate JSON file
2. Add the value to the `values` array
3. Maintain hierarchical structure if applicable
4. Update this README if adding new concepts

### Adding Fields

To add a new semantic field:

1. Create a new JSON file (e.g., `language.json`)
2. Follow the schema structure above
3. Add entry to `schema/registry.json`
4. Update this README
5. Consider backward compatibility

## Validation Rules

### Value Matching
- Values must match **exactly** (after normalization)
- Whitespace is normalized
- Hierarchy separators are normalized to `→`
- Case is preserved (schemas define canonical case)

### Required Fields
Complete descriptors **must** include:
- `domain`
- `intent`

Optional fields can be omitted.

### Custom Fields
Fields not in the schema are allowed but:
- Will not be validated
- Will trigger warnings
- Should be used sparingly

## Version History

### v1 (Current)
- Initial schema release
- 5 core fields: domain, intent, tone, audience, stability
- Hierarchical value support
- Required/optional field distinction

## Future Versions

When creating v2:
- New directory: `schema/v2/`
- Update `schema/registry.json`
- Maintain backward compatibility where possible
- Document breaking changes

## Schema Validation

All schemas are validated on load for:
- Required keys (`version`, `required`, `description`, `values`)
- Valid JSON structure
- Version matching

Invalid schemas will raise `SchemaError` with helpful messages.

## Questions?

See the main documentation:
- [Philosophy](../../docs/philosophy.md)
- [Design Principles](../../docs/design_principles.md)
- [Schema Versioning](../../docs/schema_versioning.md)
- [FAQ](../../docs/faq.md)
