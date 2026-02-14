from typing import Any, Callable

from pda.analyzer.base import BaseAnalyzer
from pda.types import AnyT


def lazy_execution(function: Callable[..., AnyT]) -> Callable[..., Any]:
    def wrapper(self: BaseAnalyzer[Any, AnyT], *args: Any, **kwargs: Any) -> AnyT:
        self._analyze_if_needed()  # pylint: disable=protected-access
        return function(self, *args, **kwargs)

    return wrapper
