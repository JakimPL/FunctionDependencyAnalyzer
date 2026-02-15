from collections.abc import Hashable, Iterable
from pathlib import Path
from typing import TypeAlias, TypeVar, Union

from anytree import NodeMixin

AnyT = TypeVar("AnyT")
AnyT_co = TypeVar("AnyT_co", covariant=True)
AnyNodeT = TypeVar("AnyNodeT", bound=NodeMixin)

Pathlike: TypeAlias = Union[str, Path]
PathInput: TypeAlias = Union[Pathlike, Iterable[Pathlike]]
HashableT = TypeVar("HashableT", bound=Hashable)
