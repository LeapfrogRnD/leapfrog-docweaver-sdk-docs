from typing import Any, TypeVar

from pydantic import BaseModel

from leapx.common.observability import observe
from leapx.services.schema_generator.model_builder import PydanticModelBuilder

T = TypeVar("T", bound=BaseModel)


@observe(capture_input=True, capture_output=False)
def create_model(
    schema: dict[str, Any],
    base_model_type: type[T] = BaseModel,
    root_schema: dict[str, Any] | None = None,
    allow_undefined_array_items: bool = False,
    allow_undefined_type: bool = False,
) -> type[T]:
    """
    Create a Pydantic model from a JSON Schema.

    Args:
        schema: The JSON Schema to convert
        root_schema: The root schema containing definitions.
                    Defaults to schema if not provided.
        allow_undefined_array_items: If True, allows arrays without items schema
        allow_undefined_type: If True, allows schemas without an explicit type

    Returns:
        A Pydantic model class

    Raises:
        SchemaError: If the schema is invalid
        JsonSchemaTypeError: If an unsupported type is encountered
        CombinerError: If there's an error in schema combiners
        ReferenceError: If there's an error resolving references
    """
    builder = PydanticModelBuilder(base_model_type=base_model_type)
    return builder.create_pydantic_model(
        schema, root_schema, allow_undefined_array_items, allow_undefined_type
    )
