#!/usr/bin/env python3
"""
Schema Migration Helper for Semantic Dropdown Search.

Safely migrates semantic descriptors between schema versions.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

from core.validate import SchemaValidator
from core.normalize import normalize_descriptor
from core.errors import ValidationError


class MigrationError(Exception):
    pass


def load_descriptor(path: Path) -> Dict[str, str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise MigrationError("Descriptor must be a JSON object")
        return data
    except json.JSONDecodeError as e:
        raise MigrationError(f"Invalid JSON: {e}")


def load_migration_map(path: Path) -> Dict[str, str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            mapping = json.load(f)
        if not isinstance(mapping, dict):
            raise MigrationError("Migration map must be a JSON object")
        return mapping
    except json.JSONDecodeError as e:
        raise MigrationError(f"Invalid migration map JSON: {e}")


def migrate_descriptor(
    descriptor: Dict[str, str],
    mapping: Dict[str, str]
) -> Dict[str, str]:
    migrated = {}

    for field, value in descriptor.items():
        new_field = mapping.get(field, field)
        if new_field in migrated:
            raise MigrationError(
                f"Field collision after migration: '{new_field}'"
            )
        migrated[new_field] = value

    return migrated


def main():
    if len(sys.argv) != 5:
        print(
            "Usage: migration_helper.py "
            "<descriptor.json> <from_version> <to_version> <mapping.json>",
            file=sys.stderr,
        )
        sys.exit(1)

    descriptor_path = Path(sys.argv[1])
    from_version = sys.argv[2]
    to_version = sys.argv[3]
    mapping_path = Path(sys.argv[4])

    descriptor = load_descriptor(descriptor_path)
    mapping = load_migration_map(mapping_path)

    migrated = migrate_descriptor(descriptor, mapping)
    migrated = normalize_descriptor(migrated, strict=True)

    validator = SchemaValidator(version=to_version)
    result = validator.validate_complete_descriptor(migrated)

    if not result:
        raise ValidationError(
            "Migration produced invalid descriptor",
            errors=result.errors,
            warnings=result.warnings,
        )

    output = {
        "from_version": from_version,
        "to_version": to_version,
        "descriptor": migrated,
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (MigrationError, ValidationError) as e:
        print(f"Migration failed: {e}", file=sys.stderr)
        sys.exit(1)
