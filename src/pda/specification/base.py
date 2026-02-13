from typing import Any

from pydantic import BaseModel, ConfigDict


class Specification(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
        frozen=True,
        use_enum_values=True,
    )

    def __init__(self, **data: Any) -> None:
        if type(self) is Specification:  # pylint: disable=unidiomatic-typecheck
            raise TypeError("Specification cannot be instantiated directly.")

        super().__init__(**data)
