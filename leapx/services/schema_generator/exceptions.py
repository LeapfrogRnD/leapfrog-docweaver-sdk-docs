from leapx.common.exceptions.base import LeapXError


class SchemaError(LeapXError):
    """Base class for schema-related errors"""

    pass


class JsonSchemaTypeError(SchemaError):
    """Invalid or unsupported type"""

    pass


class CombinerError(SchemaError):
    """Error in schema combiners"""

    pass


class ReferenceError(SchemaError):
    """Error in schema references"""

    pass
