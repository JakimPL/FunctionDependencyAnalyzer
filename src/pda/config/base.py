from typing import Any

from pydantic import BaseModel, ConfigDict


class BaseConfig(BaseModel):
    """
    Base configuration class for Python Dependency Analyzer.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
        use_enum_values=True,
    )

    def __init__(self, **data: Any) -> None:
        if type(self) is BaseConfig:  # pylint: disable=unidiomatic-typecheck
            raise TypeError("BaseConfig cannot be instantiated directly.")

        super().__init__(**data)
