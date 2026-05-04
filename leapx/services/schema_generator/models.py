from dataclasses import dataclass


@dataclass
class SchemaType:
    """Represents a JSON Schema type"""

    name: str
    format: str | None = None


@dataclass
class FieldConstraints:
    """Represents JSON Schema field constraints"""

    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None
    minimum: float | None = None
    maximum: float | None = None
    exclusive_minimum: float | None = None
    exclusive_maximum: float | None = None
    multiple_of: float | None = None
    min_items: int | None = None
    max_items: int | None = None
    unique_items: bool = False


@dataclass
class CombinerSchema:
    """Represents a JSON Schema combiner"""

    type: str  # 'allOf', 'anyOf', 'oneOf'
    schemas: list[dict]
    root_schema: dict
