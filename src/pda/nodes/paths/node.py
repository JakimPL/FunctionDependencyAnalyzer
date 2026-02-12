from __future__ import annotations

from pathlib import Path
from typing import Optional

from anytree import NodeMixin


class PathNode(NodeMixin):  # type: ignore[misc]
    def __init__(
        self,
        filepath: Path,
        parent: Optional[PathNode] = None,
    ) -> None:
        self.filepath: Path = filepath
        self.parent: Optional[PathNode] = parent

        self._has_init: bool = (filepath / "__init__.py").exists() if filepath.is_dir() else False
        self._is_package: bool = False

    def __repr__(self) -> str:
        return f"PathNode(filepath={self.filepath})"

    @property
    def name(self) -> str:
        return self.filepath.name

    @property
    def is_file(self) -> bool:
        return self.filepath.is_file()

    @property
    def is_python_file(self) -> bool:
        return self.is_file and self.filepath.suffix.lower() == ".py"

    @property
    def is_directory(self) -> bool:
        return self.filepath.is_dir()

    @property
    def is_init(self) -> bool:
        return self.filepath.name == "__init__.py"

    @property
    def is_package(self) -> bool:
        return self._is_package

    @is_package.setter
    def is_package(self, value: bool) -> None:
        self._is_package = value

    @property
    def has_init(self) -> bool:
        return self._has_init

    def mark_as_package_if_applicable(self) -> None:
        if not self.is_directory:
            return

        if self._has_init:
            self._is_package = True
            return

        if self.has_python_files_in_tree():
            self._is_package = True
            return

        self._is_package = False

    def has_python_files_in_tree(self) -> bool:
        for child in self.children:
            if child.is_python_file:
                return True

            if child.is_directory and child.is_package:
                return True

        return False
