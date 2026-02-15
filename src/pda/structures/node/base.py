from __future__ import annotations

from collections.abc import Iterable
from typing import Callable, Generic, Optional, Tuple, Type, Union

from anytree import NodeMixin

from pda.types import AnyT


class BaseNode(NodeMixin, Generic[AnyT]):  # type: ignore[misc]
    def __init__(self, item: AnyT, *, parent: Optional[BaseNode[AnyT]] = None) -> None:
        super().__init__()
        self.item: AnyT = item
        self.parent: Optional[BaseNode[AnyT]] = parent

    def has_ancestor_matching(self, predicate: Callable[[BaseNode[AnyT]], bool]) -> bool:
        current = self.parent
        while current:
            if predicate(current):
                return True

            current = current.parent

        return False

    def has_ancestor(self, ancestor: Union[BaseNode[AnyT], Iterable[BaseNode[AnyT]]]) -> bool:
        ancestors = {ancestor} if isinstance(ancestor, BaseNode) else set(ancestor)
        return self.has_ancestor_matching(lambda node: node in ancestors)

    def has_ancestor_of_type(
        self,
        ancestor_type: Union[Type[BaseNode[AnyT]], Tuple[Type[BaseNode[AnyT]], ...]],
    ) -> bool:
        return self.has_ancestor_matching(lambda node: isinstance(node, ancestor_type))

    def has_ancestor_of_id(self, items: Iterable[AnyT]) -> bool:
        if not isinstance(items, Iterable):
            raise ValueError(f"Expected an iterable of items, got {type(items)}")

        item_ids = {id(item) for item in items}
        return self.has_ancestor_matching(lambda node: id(node.item) in item_ids)
