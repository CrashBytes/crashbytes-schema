"""crashbytes-schema — Zero-dependency schema validation for Python."""

from crashbytes_schema._errors import ParseResult, SchemaError, ValidationError
from crashbytes_schema._schemas import (
    ArraySchema,
    BoolSchema,
    IntSchema,
    LiteralSchema,
    NumberSchema,
    ObjectSchema,
    OptionalSchema,
    Schema,
    SchemaBuilder,
    StringSchema,
    UnionSchema,
)

__version__ = "1.1.0"

s = SchemaBuilder()

__all__ = [
    "ArraySchema",
    "BoolSchema",
    "IntSchema",
    "LiteralSchema",
    "NumberSchema",
    "ObjectSchema",
    "OptionalSchema",
    "ParseResult",
    "Schema",
    "SchemaBuilder",
    "SchemaError",
    "StringSchema",
    "UnionSchema",
    "ValidationError",
    "__version__",
    "s",
]
