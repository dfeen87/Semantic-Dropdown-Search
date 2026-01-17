"""
Schema validation for Semantic Dropdown Search.

This module validates semantic descriptors against versioned JSON schemas.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of schema validation."""
    valid: bool
    errors: List[str]
    warnings: List[str]
    
    def __bool__(self):
        return self.valid
    
    def __str__(self):
        """Human-readable validation result."""
        if self.valid:
            msg = "✓ Validation passed"
            if self.warnings:
                msg += f" (with {len(self.warnings)} warnings)"
            return msg
        else:
            msg = f"✗ Validation failed with {len(self.errors)} error(s)"
            for error in self.errors:
                msg += f"\n  • {error}"
            if self.warnings:
                msg += f"\n\nWarnings:"
                for warning in self.warnings:
                    msg += f"\n  • {warning}"
            return msg


class SchemaValidator:
    """Validates semantic descriptors against schema definitions."""
    
    def __init__(self, schema_dir: Path = None, version: str = "v1"):
        """
        Initialize validator with schema directory.
        
        Args:
            schema_dir: Path to schema directory. Defaults to schema/{version}/
            version: Schema version to validate against
        """
        self.version = version
        
        if schema_dir is None:
            # Default to schema/{version}/ relative to this file
            schema_dir = Path(__file__).parent.parent / "schema" / version
        
        self.schema_dir = Path(schema_dir)
        self._schemas: Dict[str, Dict] = {}
        self._load_schemas()
    
    def _validate_schema_structure(self, schema: Dict, schema_file: Path):
        """
        Validate that a schema has required structure.
        
        Args:
            schema: Schema dictionary to validate
            schema_file: Path to schema file (for error messages)
            
        Raises:
            ValueError: If schema structure is invalid
        """
        # Check for required keys
        if "values" not in schema:
            raise ValueError(
                f"Schema {schema_file.name} missing required 'values' key"
            )
        
        # Check schema version matches expected version
        schema_version = schema.get("version")
        if schema_version and schema_version != self.version:
            raise ValueError(
                f"Schema {schema_file.name} declares version '{schema_version}' "
                f"but loaded into '{self.version}' validator"
            )
        
        # Validate values is a list
        if not isinstance(schema["values"], list):
            raise ValueError(
                f"Schema {schema_file.name} 'values' must be a list"
            )
    
    def _load_schemas(self):
        """Load all JSON schemas from schema directory."""
        if not self.schema_dir.exists():
            raise FileNotFoundError(f"Schema directory not found: {self.schema_dir}")
        
        schema_files = list(self.schema_dir.glob("*.json"))
        if not schema_files:
            raise ValueError(f"No schema files found in {self.schema_dir}")
        
        for schema_file in schema_files:
            field_name = schema_file.stem  # e.g., "domain" from "domain.json"
            
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schema = json.load(f)
                
                # Validate schema structure before accepting it
                self._validate_schema_structure(schema, schema_file)
                
                self._schemas[field_name] = schema
                
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in {schema_file.name}: {e}")
    
    def get_schema(self, field_name: str) -> Optional[Dict]:
        """Get schema for a specific field."""
        return self._schemas.get(field_name)
    
    def get_valid_values(self, field_name: str) -> Set[str]:
        """
        Get all valid values for a field.
        
        Args:
            field_name: Name of the semantic field
            
        Returns:
            Set of valid values (flattened hierarchy)
        """
        schema = self.get_schema(field_name)
        if not schema:
            return set()
        
        return self._extract_values(schema.get('values', []))
    
    def _extract_values(self, values: List, prefix: str = None) -> Set[str]:
        """
        Recursively extract all valid values from hierarchical schema.
        
        Args:
            values: List of values or nested dictionaries
            prefix: Current hierarchical prefix (e.g., "Science")
            
        Returns:
            Set of all valid values including hierarchical paths
        """
        result = set()
        
        for item in values:
            if isinstance(item, str):
                # Simple string value
                if prefix:
                    result.add(f"{prefix} → {item}")
                else:
                    result.add(item)
                    
            elif isinstance(item, dict):
                # Hierarchical structure like {"Science": ["Biology", "Physics"]}
                for key, children in item.items():
                    # Add the parent key itself
                    if prefix:
                        full_key = f"{prefix} → {key}"
                    else:
                        full_key = key
                    result.add(full_key)
                    
                    # Recursively process children with current key as prefix
                    if isinstance(children, list):
                        result.update(self._extract_values(children, prefix=full_key))
        
        return result
    
    def explain_invalid(self, field_name: str, value: str) -> str:
        """
        Generate human-readable explanation for why a value is invalid.
        
        Args:
            field_name: Name of the semantic field
            value: Invalid value
            
        Returns:
            Human-readable explanation string
        """
        schema = self.get_schema(field_name)
        
        if not schema:
            return (
                f"The field '{field_name}' is not recognized. "
                f"Available fields are: {', '.join(sorted(self._schemas.keys()))}"
            )
        
        valid_values = self.get_valid_values(field_name)
        
        # Find similar values for suggestions (simple string matching)
        suggestions = [v for v in valid_values if value.lower() in v.lower()]
        if not suggestions:
            # Try partial matching
            suggestions = [v for v in valid_values if any(
                part.lower() in v.lower() for part in value.split()
            )]
        
        explanation = (
            f"The value '{value}' is not allowed for field '{field_name}'.\n\n"
        )
        
        if suggestions:
            explanation += "Did you mean one of these?\n"
            for suggestion in sorted(suggestions)[:5]:  # Show top 5 suggestions
                explanation += f"  • {suggestion}\n"
        else:
            explanation += f"Allowed values for '{field_name}' include:\n"
            for allowed in sorted(valid_values)[:10]:  # Show first 10
                explanation += f"  • {allowed}\n"
            if len(valid_values) > 10:
                explanation += f"  ... and {len(valid_values) - 10} more\n"
        
        return explanation.strip()
    
    def validate_field(self, field_name: str, value: str) -> ValidationResult:
        """
        Validate a single field value against its schema.
        
        Args:
            field_name: Name of the semantic field (e.g., "domain")
            value: Value to validate
            
        Returns:
            ValidationResult with validation status
        """
        errors = []
        warnings = []
        
        # Check if schema exists
        schema = self.get_schema(field_name)
        if not schema:
            errors.append(
                f"Unknown field: '{field_name}'. "
                f"Available fields: {', '.join(sorted(self._schemas.keys()))}"
            )
            return ValidationResult(valid=False, errors=errors, warnings=warnings)
        
        # Check if value is in valid set
        valid_values = self.get_valid_values(field_name)
        if value not in valid_values:
            errors.append(self.explain_invalid(field_name, value))
            return ValidationResult(valid=False, errors=errors, warnings=warnings)
        
        return ValidationResult(valid=True, errors=errors, warnings=warnings)
    
    def validate_values(self, descriptor: Dict[str, str]) -> ValidationResult:
        """
        Validate only the VALUES in a descriptor (does not check completeness).
        
        Use this when you want to validate partial descriptors or
        when required fields are not yet filled in.
        
        Args:
            descriptor: Dictionary mapping field names to values
            
        Returns:
            ValidationResult with validation status
        """
        errors = []
        warnings = []
        
        # Check for unknown fields
        known_fields = set(self._schemas.keys())
        provided_fields = set(descriptor.keys())
        unknown = provided_fields - known_fields
        
        if unknown:
            warnings.append(
                f"Unknown fields will be ignored: {', '.join(sorted(unknown))}"
            )
        
        # Validate each provided field
        for field_name, value in descriptor.items():
            if field_name in known_fields:
                result = self.validate_field(field_name, value)
                errors.extend(result.errors)
                warnings.extend(result.warnings)
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def get_required_fields(self) -> Set[str]:
        """
        Get set of required fields based on schemas.
        
        Returns:
            Set of field names that are marked as required
        """
        required = set()
        for field_name, schema in self._schemas.items():
            if schema.get('required', False):
                required.add(field_name)
        return required
    
    def validate_complete_descriptor(self, descriptor: Dict[str, str]) -> ValidationResult:
        """
        Validate a COMPLETE semantic descriptor (checks values AND completeness).
        
        This is the primary validation method that should be used for
        finalized descriptors. It ensures:
        1. All required fields are present
        2. All values are valid according to schemas
        
        Args:
            descriptor: Dictionary mapping field names to values
            
        Returns:
            ValidationResult indicating if descriptor is valid and complete
        """
        errors = []
        warnings = []
        
        # Check for missing required fields
        required = self.get_required_fields()
        provided = set(descriptor.keys())
        missing = required - provided
        
        if missing:
            errors.append(
                f"Missing required fields: {', '.join(sorted(missing))}"
            )
        
        # Validate all provided values
        value_result = self.validate_values(descriptor)
        errors.extend(value_result.errors)
        warnings.extend(value_result.warnings)
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def validate_descriptor(self, descriptor: Dict[str, str]) -> ValidationResult:
        """
        Validate a semantic descriptor (default: complete validation).
        
        This is a convenience wrapper around validate_complete_descriptor().
        For partial validation, use validate_values() explicitly.
        
        Args:
            descriptor: Dictionary mapping field names to values
            
        Returns:
            ValidationResult
        """
        return self.validate_complete_descriptor(descriptor)


def validate(descriptor: Dict[str, str], schema_version: str = "v1", 
             partial: bool = False) -> ValidationResult:
    """
    Convenience function to validate a descriptor.
    
    Args:
        descriptor: Semantic descriptor to validate
        schema_version: Schema version to validate against
        partial: If True, only validate values (not completeness)
        
    Returns:
        ValidationResult
    """
    validator = SchemaValidator(version=schema_version)
    
    if partial:
        return validator.validate_values(descriptor)
    else:
        return validator.validate_complete_descriptor(descriptor)
