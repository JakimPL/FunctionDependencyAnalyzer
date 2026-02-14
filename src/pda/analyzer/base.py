from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, Optional

from pda.config import ConfigT
from pda.tools.logger import logger
from pda.types import AnyT, Pathlike


class BaseAnalyzer(ABC, Generic[ConfigT, AnyT]):
    def __init__(
        self,
        config: Optional[ConfigT] = None,
        project_root: Optional[Pathlike] = None,
        package: Optional[str] = None,
    ) -> None:
        self.config = config or self.default_config()
        self._project_root = Path(project_root).resolve() if project_root is not None else None
        self._package = package

    @abstractmethod
    def __bool__(self) -> bool:
        """Return True if the analyzer has processed data, False otherwise."""

    def __call__(self, *, refresh: bool = False) -> AnyT:
        return self._analyze_if_needed(refresh=refresh)

    @abstractmethod
    def clear(self) -> None:
        """Clear the analyzer's internal state."""

    @abstractmethod
    def _analyze_if_needed(self, *, refresh: bool = False) -> AnyT:
        """Perform analysis if needed, optionally refreshing the data."""

    @property
    def project_root(self) -> Optional[Path]:
        return self._project_root

    @project_root.setter
    def project_root(self, value: Optional[Pathlike]) -> None:
        self._project_root = Path(value).resolve() if value is not None else None
        if self:
            logger.info("Project root changed. Clearing the graph and modules")

        self.clear()

    @property
    def package(self) -> Optional[str]:
        return self._package

    @package.setter
    def package(self, value: Optional[str]) -> None:
        self._package = value
        if self:
            logger.info("Package changed. Clearing the graph and modules.")

        self.clear()

    @classmethod
    @abstractmethod
    def default_config(cls) -> ConfigT:
        """Return the default configuration for this analyzer."""
