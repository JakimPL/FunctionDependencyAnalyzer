from abc import ABC

from pydantic import BaseModel, ConfigDict


class BaseConfig(BaseModel, ABC):
    """
    Base configuration class for Python Dependency Analyzer.
    """

    model_config = ConfigDict(
        extra="forbid",
        use_enum_values=True,
    )
