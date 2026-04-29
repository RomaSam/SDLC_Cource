from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, Field, field_validator, model_validator

MAX_DURATION_MINUTES = 600
MAX_SEATS = 10_000

class _ScreeningBase(BaseModel):

    # check_fields=False is required because the validated fields are defined on
    # subclasses, not on _ScreeningBase itself. Without it Pydantic v2 raises
    # PydanticUserError at import time and the application refuses to start.
    @field_validator("screening_date", mode="before", check_fields=False)
    @classmethod
    def validate_date(cls, v: object) -> str | None:
        if v is None:
            return v
        try:
            datetime.strptime(str(v), "%Y-%m-%d")
        except ValueError:
            raise ValueError("Must be a valid calendar date in YYYY-MM-DD format")
        return str(v)

    @field_validator("begins_at", mode="before", check_fields=False)
    @classmethod
    def validate_time(cls, v: object) -> str | None:
        if v is None:
            return v
        try:
            datetime.strptime(str(v), "%H:%M")
        except ValueError:
            raise ValueError("Must be a valid time in HH:MM format")
        return str(v)


class CreateScreeningRequest(_ScreeningBase):
    name: Annotated[str, Field(min_length=1, max_length=200)]
    genre: Annotated[str | None, Field(default=None, max_length=100)]
    duration_minutes: Annotated[int, Field(gt=0, le=MAX_DURATION_MINUTES)]
    screening_date: Annotated[str, Field(min_length=10, max_length=10)]
    begins_at: Annotated[str, Field(min_length=5, max_length=5)]
    hall: Annotated[str, Field(min_length=1, max_length=50)]
    seats: Annotated[int, Field(gt=0, le=MAX_SEATS)]


class PatchScreeningRequest(_ScreeningBase):
    name: Annotated[str | None, Field(default=None, min_length=1, max_length=200)]
    genre: Annotated[str | None, Field(default=None, max_length=100)]
    duration_minutes: Annotated[int | None, Field(default=None, gt=0, le=MAX_DURATION_MINUTES)]
    screening_date: Annotated[str | None, Field(default=None, min_length=10, max_length=10)]
    begins_at: Annotated[str | None, Field(default=None, min_length=5, max_length=5)]
    hall: Annotated[str | None, Field(default=None, min_length=1, max_length=50)]
    seats: Annotated[int | None, Field(default=None, gt=0, le=MAX_SEATS)]

    @model_validator(mode="after")
    def at_least_one_field(self) -> "PatchScreeningRequest":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided for a partial update")
        return self
