from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_snake


class BaseSchema(BaseModel):
    """Base schema with common configurations for all models"""

    model_config = ConfigDict(
        alias_generator=to_snake,
        populate_by_name=True,
        validate_assignment=True,
        frozen=False,
        strict=True,
        json_schema_extra={"examples": []},
        ser_json_timedelta="iso8601",
        ser_json_bytes="base64",
        validate_default=True,
        extra="forbid",
    )
