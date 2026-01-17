"""
Serialization formats for Semantic Dropdown Search.

This module handles converting indexed text to/from various formats
for storage and interchange.

Serialization is intentionally dumb and deterministic.
No validation, ranking, or inference is performed here.
"""

import json
import csv
from typing import List, Dict, Any, Optional
from pathlib import Path
from io import StringIO

from .index_text import IndexedText
from ..core.descriptor import SemanticDescriptor
from ..core.errors import IndexingError


class Serializer:
    """Base serializer interface."""

    @staticmethod
    def serialize(items: List[IndexedText]) -> str:
        raise NotImplementedError

    @staticmethod
    def deserialize(data: str) -> List[IndexedText]:
        raise NotImplementedError

    @staticmethod
    def serialize_to_file(items: List[IndexedText], filepath: Path):
        raise NotImplementedError

    @staticmethod
    def deserialize_from_file(filepath: Path) -> List[IndexedText]:
        raise NotImplementedError


# -------------------------
# JSON SERIALIZATION
# -------------------------

class JSONSerializer(Serializer):
    """JSON serialization for indexed texts."""

    @staticmethod
    def serialize(items: List[IndexedText], indent: int = 2) -> str:
        return json.dumps(
            [item.to_dict() for item in items],
            indent=indent,
            ensure_ascii=False,
        )

    @staticmethod
    def deserialize(data: str) -> List[IndexedText]:
        items_data = json.loads(data)
        return [IndexedText.from_dict(d) for d in items_data]

    @staticmethod
    def serialize_to_file(
        items: List[IndexedText],
        filepath: Path,
        indent: int = 2,
    ):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(
                [item.to_dict() for item in items],
                f,
                indent=indent,
                ensure_ascii=False,
            )

    @staticmethod
    def deserialize_from_file(filepath: Path) -> List[IndexedText]:
        with open(filepath, "r", encoding="utf-8") as f:
            return [
                IndexedText.from_dict(d)
                for d in json.load(f)
            ]


# -------------------------
# NDJSON / JSONL
# -------------------------

class NDJSONSerializer(Serializer):
    """
    Newline-delimited JSON (NDJSON / JSONL).

    Each line is a complete JSON object.
    Suitable for streaming and append-only storage.
    """

    @staticmethod
    def serialize(items: List[IndexedText]) -> str:
        return "\n".join(
            json.dumps(item.to_dict(), ensure_ascii=False)
            for item in items
        )

    @staticmethod
    def deserialize(data: str) -> List[IndexedText]:
        items = []
        for line in data.splitlines():
            if line.strip():
                items.append(
                    IndexedText.from_dict(json.loads(line))
                )
        return items

    @staticmethod
    def serialize_to_file(items: List[IndexedText], filepath: Path):
        with open(filepath, "w", encoding="utf-8") as f:
            for item in items:
                f.write(
                    json.dumps(item.to_dict(), ensure_ascii=False) + "\n"
                )

    @staticmethod
    def deserialize_from_file(filepath: Path) -> List[IndexedText]:
        items = []
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    items.append(
                        IndexedText.from_dict(json.loads(line))
                    )
        return items

    @staticmethod
    def append_to_file(item: IndexedText, filepath: Path):
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(
                json.dumps(item.to_dict(), ensure_ascii=False) + "\n"
            )


# -------------------------
# CSV SERIALIZATION
# -------------------------

class CSVSerializer(Serializer):
    """
    CSV serialization for indexed texts.

    Descriptor fields are flattened.
    Metadata is stored as a JSON string.
    """

    FIELDNAMES = [
        "id",
        "text",
        "domain",
        "intent",
        "tone",
        "audience",
        "stability",
        "metadata",
        "created_at",
        "updated_at",
        "content_hash",
    ]

    @staticmethod
    def _flatten(item: IndexedText) -> Dict[str, str]:
        descriptor = item.descriptor.to_dict()

        return {
            "id": item.id,
            "text": item.text,
            "domain": descriptor.get("domain", ""),
            "intent": descriptor.get("intent", ""),
            "tone": descriptor.get("tone", ""),
            "audience": descriptor.get("audience", ""),
            "stability": descriptor.get("stability", ""),
            "metadata": json.dumps(item.metadata, ensure_ascii=False),
            "created_at": item.created_at.isoformat(),
            "updated_at": item.updated_at.isoformat(),
            "content_hash": item.content_hash,
        }

    @staticmethod
    def _unflatten(row: Dict[str, str]) -> IndexedText:
        descriptor_data = {
            k: row[k]
            for k in ["domain", "intent", "tone", "audience", "stability"]
            if row.get(k)
        }

        return IndexedText.from_dict({
            "id": row["id"],
            "text": row["text"],
            "descriptor": descriptor_data,
            "metadata": json.loads(row.get("metadata", "{}")),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "content_hash": row.get("content_hash", ""),
        })

    @staticmethod
    def serialize(items: List[IndexedText]) -> str:
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=CSVSerializer.FIELDNAMES)
        writer.writeheader()

        for item in items:
            writer.writerow(CSVSerializer._flatten(item))

        return output.getvalue()

    @staticmethod
    def deserialize(data: str) -> List[IndexedText]:
        reader = csv.DictReader(StringIO(data))
        return [CSVSerializer._unflatten(row) for row in reader]

    @staticmethod
    def serialize_to_file(items: List[IndexedText], filepath: Path):
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSVSerializer.FIELDNAMES)
            writer.writeheader()
            for item in items:
                writer.writerow(CSVSerializer._flatten(item))

    @staticmethod
    def deserialize_from_file(filepath: Path) -> List[IndexedText]:
        with open(filepath, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            return [CSVSerializer._unflatten(row) for row in reader]


# -------------------------
# FORMAT REGISTRY
# -------------------------

SERIALIZERS = {
    "json": JSONSerializer,
    "ndjson": NDJSONSerializer,
    "jsonl": NDJSONSerializer,
    "csv": CSVSerializer,
}


# -------------------------
# CONVENIENCE FUNCTIONS
# -------------------------

def serialize(
    items: List[IndexedText],
    format: str = "json",
    **kwargs,
) -> str:
    serializer = SERIALIZERS.get(format.lower())
    if not serializer:
        raise IndexingError(
            f"Unknown format '{format}'. "
            f"Available formats: {', '.join(SERIALIZERS)}"
        )
    return serializer.serialize(items, **kwargs)


def deserialize(data: str, format: str = "json") -> List[IndexedText]:
    serializer = SERIALIZERS.get(format.lower())
    if not serializer:
        raise IndexingError(
            f"Unknown format '{format}'. "
            f"Available formats: {', '.join(SERIALIZERS)}"
        )
    return serializer.deserialize(data)


def save_to_file(
    items: List[IndexedText],
    filepath: Path,
    format: Optional[str] = None,
    **kwargs,
):
    filepath = Path(filepath)
    fmt = format or filepath.suffix.lstrip(".") or "json"

    serializer = SERIALIZERS.get(fmt.lower())
    if not serializer:
        raise IndexingError(
            f"Unknown format '{fmt}'. "
            f"Available formats: {', '.join(SERIALIZERS)}"
        )

    serializer.serialize_to_file(items, filepath, **kwargs)


def load_from_file(
    filepath: Path,
    format: Optional[str] = None,
) -> List[IndexedText]:
    filepath = Path(filepath)
    fmt = format or filepath.suffix.lstrip(".") or "json"

    serializer = SERIALIZERS.get(fmt.lower())
    if not serializer:
        raise IndexingError(
            f"Unknown format '{fmt}'. "
            f"Available formats: {', '.join(SERIALIZERS)}"
        )

    return serializer.deserialize_from_file(filepath)
