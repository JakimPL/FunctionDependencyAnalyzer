from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from pda.models.scope.node import ScopeNode
from pda.structures.forest.base import Forest


class ScopeForest(Forest[ScopeNode[Any]]):
    """
    A forest of scope trees, typically containing multiple module scopes.

    This is used when analyzing multiple Python files, where each file
    has its own module scope as a root.
    """

    def __init__(
        self,
        scopes: Iterable[ScopeNode[Any]],
        *,
        detach_from_parents: bool = False,
    ) -> None:
        """
        Initialize a scope forest.

        Args:
            scopes: Iterable of ScopeNode objects (typically module scopes).
            detach_from_parents: Whether to detach roots from their parents.
                For scope forests, this is typically False since module scopes
                should not have parents.
        """
        super().__init__(scopes, detach_from_parents=detach_from_parents)

    def edge_label(self, from_node: ScopeNode[Any], to_node: ScopeNode[Any]) -> str:
        """
        Get the edge label between two scopes.

        Args:
            from_node: The parent scope.
            to_node: The child scope.

        Returns:
            A label describing the relationship.
        """
        return f"{from_node.scope_type.value}:{from_node.label} → {to_node.scope_type.value}:{to_node.label}"
