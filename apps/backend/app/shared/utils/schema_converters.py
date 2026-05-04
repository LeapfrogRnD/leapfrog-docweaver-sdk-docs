"""Schema conversion utilities."""

from typing import Any

from app.shared.utils.utils import to_snake_case


def convert_extraction_schema_to_json_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """
    Convert extraction schema format to JSON schema format.

    Args:
        schema: Schema with fields array

    Returns:
        JSON schema compatible with the pipeline
    """
    properties = {}
    required = []
    type_mapping = {
        "integer": "integer",
        "float": "number",
        "number": "number",
        "boolean": "boolean",
        "text": "string",
        "object": "object",
        "dict": "object",
    }
    for field in schema:
        field_name = to_snake_case(field.get("name"))
        field_type = field.get("type", "string")
        field_description = field.get("description", "")

        json_type = type_mapping.get(field_type, "string")
        properties[field_name] = {
            "type": json_type,
            "name": field_name,
            "description": field_description,
        }

        if field.get("required", False):
            required.append(field_name)

    json_schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
    }

    if required:
        json_schema["required"] = required

    return json_schema


def convert_classification_schema_to_json_schema(
    classification_schema: dict[str, Any] | list,
) -> dict[str, Any]:
    """
    Convert classification schema to JSON schema format.

    Accepts either:
    - A plain list: [{"category": "...", "fields": [...]}, ...]
    - A dict with a 'classifiers' key: {"classifiers": [...]}

    Args:
        classification_schema: Schema with classifiers array

    Returns:
        JSON schema compatible with the pipeline

    Raises:
        ValueError: If classification_schema has no classifiers
    """
    if isinstance(classification_schema, list):
        classifiers = classification_schema
    else:
        classifiers = classification_schema.get("classifiers", [])

    if not classifiers:
        raise ValueError("classification_schema must contain at least one classifier")

    schemas = {}
    required = []

    for classifier in classifiers:
        category = classifier["category"]
        fields = classifier["fields"]

        enum_values = []
        descriptions = []

        for field in fields:
            name = field.get("name")
            enum_values.append(name)

            # Build human-friendly description using available keys
            desc_parts = [name]
            if field.get("description"):
                desc_parts.append(field.get("description"))
            desc = ": ".join(desc_parts) if len(desc_parts) > 1 else name
            if field.get("example"):
                desc += f" (Example: {field.get('example')})"

            descriptions.append(desc)

        classifier_key = to_snake_case(category)
        required.append(classifier_key)
        schema = {
            classifier_key: {
                "type": "string",
                "enum": enum_values,
                "description": (
                    "The predicted classification for this page. "
                    f"Options: {', '.join(descriptions)}"
                ),
            },
        }
        schemas = {**schemas, **schema}

    return {
        "type": "object",
        "additionalProperties": False,
        "properties": schemas,
        "required": required,
    }
