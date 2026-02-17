from __future__ import annotations

from typing import Any, Callable, Generic, Optional, Protocol, Union

from anytree import NodeMixin

from pda.structures.node.base import Node
from pda.types import HashableT, HashableT_co


class HasAncestorCallable(Protocol, Generic[HashableT_co]):
    def __call__(self, parent: AnyNode[HashableT_co], *args: Any, **kwargs: Any) -> bool: ...


class AnyNode(Node[HashableT], NodeMixin, Generic[HashableT]):  # type: ignore[misc]
    def __init__(
        self,
        item: HashableT,
        *,
        parent: Optional[AnyNode[HashableT]] = None,
        ordinal: int = 0,
        label: Optional[str] = None,
        details: Optional[str] = None,
        level: int = 0,
        order: int = 0,
        group: Optional[str] = None,
    ) -> None:
        self.parent: Optional[AnyNode[HashableT]] = parent

        ordinal = ordinal or id(item)
        label = label or str(item)
        level = level if parent is None else parent.level + 1
        super().__init__(
            item,
            ordinal=ordinal,
            label=label,
            details=details,
            level=level,
            order=order,
            group=group,
        )

    def has_ancestor(
        self,
        predicate: Union[Callable[[HashableT], bool], HasAncestorCallable[HashableT]],
        *args: Any,
        include_self: bool = False,
        **kwargs: Any,
    ) -> bool:
        current = self if include_self else self.parent
        while current:
            if predicate(current, *args, **kwargs):
                return True

            current = current.parent

        return False
