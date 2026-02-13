"""
Semantic Descriptor object for Semantic Dropdown Search.

This module defines the core SemanticDescriptor class that represents
a semantic description of content.
"""

import json
from typing import Dict, Optional, Set, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path

from .validate import SchemaValidator, ValidationResult
from .normalize import normalize_descriptor, normalize_value
from .errors import ValidationError


@dataclass
class SemanticDescriptor:
    """
    A semantic descriptor that describes content using structured metadata.
    
    Attributes:
        domain: Content domain (e.g., "Science → Biology")
        intent: Content intent (e.g., "Research → Conceptual")
        tone: Content tone (e.g., "Analytical / Cautious")
        audience: Target audience (e.g., "Researchers")
        stability: Content stability (e.g., "Hypothesis (Not yet validated)")
        custom_fields: Additional custom fields not in standard schema
    """
    
    domain: Optional[str] = None
    intent: Optional[str] = None
    tone: Optional[str] = None
    audience: Optional[str] = None
    stability: Optional[str] = None
    custom_fields: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Normalize all fields after initialization."""
        # Build descriptor dict from standard fields
        descriptor_dict = {
            'domain': self.domain,
            'intent': self.intent,
            'tone': self.tone,
            'audience': self.audience,
            'stability': self.stability,
        }
        
        # Remove None values
        descriptor_dict = {k: v for k, v in descriptor_dict.items() if v is not None}
        
        # Add custom fields
        descriptor_dict.update(self.custom_fields)
        
        # Normalize
        normalized = normalize_descriptor(descriptor_dict, strict=True)
        
        # Update standard fields with normalized values
        self.domain = normalized.get('domain')
        self.intent = normalized.get('intent')
        self.tone = normalized.get('tone')
        self.audience = normalized.get('audience')
        self.stability = normalized.get('stability')
        
        # Update custom fields
        standard_fields = {'domain', 'intent', 'tone', 'audience', 'stability'}
        self.custom_fields = {
            k: v for k, v in normalized.items() 
            if k not in standard_fields
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'SemanticDescriptor':
        """
        Create a SemanticDescriptor from a dictionary.
        
        Args:
            data: Dictionary mapping field names to values
            
        Returns:
            SemanticDescriptor instance
        """
        # Separate standard fields from custom fields
        standard_fields = {'domain', 'intent', 'tone', 'audience', 'stability'}
        
        standard = {k: v for k, v in data.items() if k in standard_fields}
        custom = {k: v for k, v in data.items() if k not in standard_fields}
        
        return cls(
            domain=standard.get('domain'),
            intent=standard.get('intent'),
            tone=standard.get('tone'),
            audience=standard.get('audience'),
            stability=standard.get('stability'),
            custom_fields=custom
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SemanticDescriptor':
        """
        Create a SemanticDescriptor from a JSON string.
        
        Args:
            json_str: JSON string representing descriptor
            
        Returns:
            SemanticDescriptor instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @classmethod
    def from_file(cls, filepath: Path) -> 'SemanticDescriptor':
        """
        Load a SemanticDescriptor from a JSON file.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            SemanticDescriptor instance
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def to_dict(self, include_none: bool = False) -> Dict[str, str]:
        """
        Convert descriptor to dictionary.
        
        Args:
            include_none: If True, include fields with None values
            
        Returns:
            Dictionary representation
        """
        result = {
            'domain': self.domain,
            'intent': self.intent,
            'tone': self.tone,
            'audience': self.audience,
            'stability': self.stability,
        }
        
        # Add custom fields
        result.update(self.custom_fields)
        
        # Remove None values if requested
        if not include_none:
            result = {k: v for k, v in result.items() if v is not None}
        
        return result
    
    def to_json(self, indent: int = 2, include_none: bool = False) -> str:
        """
        Convert descriptor to JSON string.
        
        Args:
            indent: JSON indentation level
            include_none: If True, include fields with None values
            
        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(include_none=include_none), indent=indent)
    
    def to_file(self, filepath: Path, indent: int = 2, include_none: bool = False):
        """
        Save descriptor to a JSON file.
        
        Args:
            filepath: Path to save JSON file
            indent: JSON indentation level
            include_none: If True, include fields with None values
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(include_none=include_none), f, indent=indent)
    
    def validate(self, schema_version: str = "v1", 
                 partial: bool = False) -> ValidationResult:
        """
        Validate this descriptor against schemas.
        
        Args:
            schema_version: Schema version to validate against
            partial: If True, only validate present fields (not completeness)
            
        Returns:
            ValidationResult
        """
        validator = SchemaValidator(version=schema_version)
        
        descriptor_dict = self.to_dict(include_none=False)
        
        if partial:
            return validator.validate_values(descriptor_dict)
        else:
            return validator.validate_complete_descriptor(descriptor_dict)
    
    def is_valid(self, schema_version: str = "v1", partial: bool = False) -> bool:
        """
        Check if descriptor is valid.
        
        Args:
            schema_version: Schema version to validate against
            partial: If True, only validate present fields
            
        Returns:
            True if valid
        """
        return bool(self.validate(schema_version=schema_version, partial=partial))
    
    def validate_or_raise(self, schema_version: str = "v1", partial: bool = False):
        """
        Validate descriptor and raise exception if invalid.
        
        Args:
            schema_version: Schema version to validate against
            partial: If True, only validate present fields
            
        Raises:
            ValidationError: If validation fails
        """
        result = self.validate(schema_version=schema_version, partial=partial)
        if not result:
            raise ValidationError(
                "Descriptor validation failed",
                errors=result.errors,
                warnings=result.warnings
            )
    
    def get_field(self, field_name: str) -> Optional[str]:
        """
        Get value of a field by name.
        
        Args:
            field_name: Name of field to get
            
        Returns:
            Field value, or None if not set
        """
        field_name = field_name.lower()
        
        standard_fields = {
            'domain': self.domain,
            'intent': self.intent,
            'tone': self.tone,
            'audience': self.audience,
            'stability': self.stability,
        }
        
        if field_name in standard_fields:
            return standard_fields[field_name]
        
        return self.custom_fields.get(field_name)
    
    def set_field(self, field_name: str, value: str):
        """
        Set value of a field by name.
        
        Args:
            field_name: Name of field to set
            value: Value to set
        """
        # Normalize value
        normalized_value = normalize_value(value)
        normalized_field = field_name.lower()
        
        standard_fields = {'domain', 'intent', 'tone', 'audience', 'stability'}
        
        if normalized_field in standard_fields:
            setattr(self, normalized_field, normalized_value)
        else:
            self.custom_fields[normalized_field] = normalized_value
    
    def get_filled_fields(self) -> Set[str]:
        """
        Get set of all filled field names.
        
        Returns:
            Set of field names that have values
        """
        filled = set()
        
        if self.domain is not None:
            filled.add('domain')
        if self.intent is not None:
            filled.add('intent')
        if self.tone is not None:
            filled.add('tone')
        if self.audience is not None:
            filled.add('audience')
        if self.stability is not None:
            filled.add('stability')
        
        filled.update(self.custom_fields.keys())
        
        return filled
    
    def is_complete(self, schema_version: str = "v1") -> bool:
        """
        Check if all required fields are filled.
        
        Args:
            schema_version: Schema version to check against
            
        Returns:
            True if all required fields are present
        """
        validator = SchemaValidator(version=schema_version)
        required = validator.get_required_fields()
        filled = self.get_filled_fields()
        
        return required.issubset(filled)
    
    def __str__(self) -> str:
        """String representation of descriptor."""
        fields = []
        if self.domain:
            fields.append(f"domain: {self.domain}")
        if self.intent:
            fields.append(f"intent: {self.intent}")
        if self.tone:
            fields.append(f"tone: {self.tone}")
        if self.audience:
            fields.append(f"audience: {self.audience}")
        if self.stability:
            fields.append(f"stability: {self.stability}")
        for key, value in self.custom_fields.items():
            fields.append(f"{key}: {value}")
        
        return f"SemanticDescriptor({', '.join(fields)})"
    
    def __repr__(self) -> str:
        """Developer representation."""
        return self.__str__()
    
    def __eq__(self, other: Any) -> bool:
        """Check equality with another descriptor."""
        if not isinstance(other, SemanticDescriptor):
            return False
        
        return self.to_dict() == other.to_dict()
    
    def __hash__(self) -> int:
        """Make descriptor hashable for use in sets/dicts."""
        # Convert to tuple of sorted items for consistent hashing
        items = tuple(sorted(self.to_dict().items()))
        return hash(items)
