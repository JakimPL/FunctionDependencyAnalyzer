from __future__ import annotations

from abc import ABC, abstractmethod
from importlib.machinery import ModuleSpec
from pathlib import Path
from typing import Optional, Self, Tuple

from pydantic import Field, model_validator

from pda.constants import DELIMITER
from pda.exceptions import PDAPathResolutionError
from pda.specification.base import Specification
from pda.specification.imports.path import ImportPath
from pda.specification.modules.module.category import ModuleCategory
from pda.specification.modules.spec import find_module_spec
from pda.tools.paths import resolve_path


class BaseModule(Specification, ABC):
    """
    Base class for module specifications, containing common attributes and methods for all module types.
    This class is not meant to be instantiated directly, but rather serves as a foundation for more specific
    module specifications such as Module or UnavailableModule.
    """

    name: str = Field(description="Fully qualified module name, e.g. 'package.module'")
    package: Optional[str] = Field(default=None, description="Corresponding package name, e.g. 'package'")

    @model_validator(mode="after")
    @abstractmethod
    def validate_module(self) -> Self: ...

    @property
    def parts(self) -> Tuple[str, ...]:
        return tuple(self.name.split(DELIMITER))

    @property
    def module_name(self) -> str:
        return self.name.removesuffix(".__init__").split(DELIMITER)[-1]

    @property
    def qualified_name(self) -> str:
        return self.name.removesuffix(".__init__")

    @property
    def top_level_module(self) -> str:
        top_level = self.package or self.name
        return top_level.split(DELIMITER)[0]

    @property
    def is_top_level(self) -> bool:
        return self.name == self.top_level_module

    @property
    def is_private(self) -> bool:
        return any(part.startswith("_") and not part.startswith("__") for part in self.parts)

    @property
    def import_path(self) -> ImportPath:
        return ImportPath.from_string(self.name)

    @property
    def base_path(self) -> Path:
        spec = find_module_spec(
            self.top_level_module,
            validate_origin=False,
            expect_python=False,
        )

        path: Optional[Path] = None
        if spec and spec.origin:
            if spec.submodule_search_locations:
                path = resolve_path(spec.submodule_search_locations[0])
            else:
                path = resolve_path(spec.origin)

        if path is None:
            raise PDAPathResolutionError(
                f"Cannot determine base path for module '{self.name}' with top-level '{self.top_level_module}'"
            )

        return path.parent

    @property
    def spec(self) -> ModuleSpec:
        """
        Convert the Module instance back to a ModuleSpec for compatibility with importlib.
        """
        return find_module_spec(
            self.name,
            package=self.package,
            allow_missing_spec=False,
            raise_error=True,
            validate_origin=False,
            expect_python=False,
        )

    @abstractmethod
    def get_category(self, base_path: Optional[Path] = None) -> ModuleCategory: ...
