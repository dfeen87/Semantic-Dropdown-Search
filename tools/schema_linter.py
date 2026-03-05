#!/usr/bin/env python3
"""
Schema Linter for Semantic Dropdown Search.

Validates schema files for correctness, consistency, and v1 invariants.
"""

import json
import sys
from pathlib import Path
from typing import Set, List, Dict


REQUIRED_KEYS = {"version", "values"}


class SchemaLintError(Exception):
    pass


def load_json(path: Path) -> Dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise SchemaLintError(f"{path.name}: Invalid JSON ({e})")


def extract_values(values: List, seen: Set[str], path: str = ""):
    """
    Recursively extract values and detect duplicates.

    Duplicate detection uses the full path (e.g. "Science/Biology") so that
    the same short label can legitimately appear as both a leaf value and as
    a parent key at different levels of the hierarchy.

    A node is allowed to appear once as a string leaf (selectable without
    subcategory) AND once as a dict parent (selectable with subcategories).
    Only true duplicates — two strings or two dicts with the same full path —
    are reported as errors.
    """
    for item in values:
        full_path = ""  # will be set below for each item type

        if isinstance(item, str):
            full_path = f"{path}/{item}" if path else item
            # String leaves are tracked with a "_leaf" suffix
            leaf_key = f"{full_path}::leaf"
            if leaf_key in seen:
                raise SchemaLintError(f"Duplicate value detected: '{item}'")
            seen.add(leaf_key)

        elif isinstance(item, dict):
            for key, children in item.items():
                full_path = f"{path}/{key}" if path else key
                # Dict parents are tracked with a "_parent" suffix
                parent_key = f"{full_path}::parent"
                if parent_key in seen:
                    raise SchemaLintError(f"Duplicate value detected: '{key}'")
                seen.add(parent_key)

                if not isinstance(children, list):
                    raise SchemaLintError(
                        f"Children of '{key}' must be a list"
                    )

                extract_values(children, seen, full_path)
        else:
            raise SchemaLintError(
                f"Invalid schema entry type: {type(item).__name__}"
            )


def lint_schema_file(schema_path: Path, expected_version: str):
    schema = load_json(schema_path)

    missing = REQUIRED_KEYS - schema.keys()
    if missing:
        raise SchemaLintError(
            f"{schema_path.name}: Missing required keys: {missing}"
        )

    if schema["version"] != expected_version:
        raise SchemaLintError(
            f"{schema_path.name}: Declares version '{schema['version']}', "
            f"expected '{expected_version}'"
        )

    if not isinstance(schema["values"], list):
        raise SchemaLintError(
            f"{schema_path.name}: 'values' must be a list"
        )

    seen: Set[str] = set()
    extract_values(schema["values"], seen)


def lint_registry(schema_root: Path):
    registry_path = schema_root / "registry.json"
    if not registry_path.exists():
        raise SchemaLintError("Missing registry.json")

    registry = load_json(registry_path)

    if "versions" not in registry:
        raise SchemaLintError("registry.json missing 'versions' key")

    for version, version_info in registry["versions"].items():
        version_dir = schema_root / version
        if not version_dir.exists():
            raise SchemaLintError(
                f"Registry references missing directory: {version}"
            )

        for field in version_info.get("fields", {}).keys():
            schema_file = version_dir / f"{field}.json"
            if not schema_file.exists():
                raise SchemaLintError(
                    f"Registry references missing schema: {schema_file}"
                )


def main():
    root = Path(__file__).resolve().parents[1]
    schema_root = root / "schema"

    if not schema_root.exists():
        print("Schema directory not found.", file=sys.stderr)
        sys.exit(1)

    lint_registry(schema_root)

    for version_dir in schema_root.iterdir():
        if not version_dir.is_dir() or version_dir.name == "__pycache__":
            continue

        for schema_file in version_dir.glob("*.json"):
            if schema_file.name == "registry.json":
                continue

            lint_schema_file(schema_file, version_dir.name)

    print("✓ All schemas passed linting")


if __name__ == "__main__":
    try:
        main()
    except SchemaLintError as e:
        print(f"Schema lint failed: {e}", file=sys.stderr)
        sys.exit(1)
