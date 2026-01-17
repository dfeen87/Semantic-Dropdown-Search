"""
Custom exceptions for Semantic Dropdown Search.
"""


class SemanticDropdownError(Exception):
    """Base exception for all semantic dropdown errors."""
    pass


class ValidationError(SemanticDropdownError):
    """Raised when descriptor validation fails."""
    
    def __init__(self, message: str, errors: list = None, warnings: list = None):
        super().__init__(message)
        self.errors = errors or []
        self.warnings = warnings or []
    
    def __str__(self):
        msg = super().__str__()
        if self.errors:
            msg += "\n\nErrors:"
            for error in self.errors:
                msg += f"\n  • {error}"
        if self.warnings:
            msg += "\n\nWarnings:"
            for warning in self.warnings:
                msg += f"\n  • {warning}"
        return msg


class SchemaError(SemanticDropdownError):
    """Raised when schema definition is invalid or missing."""
    
    def __init__(self, message: str, schema_file: str = None):
        super().__init__(message)
        self.schema_file = schema_file
    
    def __str__(self):
        msg = super().__str__()
        if self.schema_file:
            msg += f" (in schema file: {self.schema_file})"
        return msg


class SchemaVersionError(SchemaError):
    """Raised when schema version mismatch occurs."""
    
    def __init__(self, expected: str, actual: str, schema_file: str = None):
        message = (
            f"Schema version mismatch: expected '{expected}', "
            f"but schema declares '{actual}'"
        )
        super().__init__(message, schema_file)
        self.expected = expected
        self.actual = actual


class NormalizationError(SemanticDropdownError):
    """Raised when normalization fails."""
    pass


class IndexingError(SemanticDropdownError):
    """Raised when indexing operations fail."""
    pass


class QueryError(SemanticDropdownError):
    """Raised when query construction or execution fails."""
    pass
