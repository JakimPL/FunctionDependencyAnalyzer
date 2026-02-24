from __future__ import annotations

from typing import Optional, Type

from pda.models.python.dump import ast_dump, ast_group, ast_label
from pda.structures import AnyNode
from pda.types import ASTT


class ASTNode(AnyNode[ASTT]):
    _ordinal_counter: int = 0

    def __init__(
        self,
        node: ASTT,
        *,
        parent: Optional[ASTNode[ASTT]] = None,
        label: Optional[str] = None,
    ) -> None:
        label = label or ast_label(node)
        details = ast_dump(node, short=True)
        group = ast_group(node)
        super().__init__(
            item=node,
            parent=parent,
            ordinal=self._ordinal(),
            label=label,
            details=details,
            group=group,
        )

    @property
    def ast(self) -> ASTT:
        return self.item

    @property
    def type(self) -> Type[ASTT]:
        return type(self.ast)

    @property
    def fqn(self) -> str:
        """
        Get the fully qualified name prefix by walking parent nodes.

        Returns:
            String like "module.path.ClassName" or "module.path".
        """
        parent_prefix = self.parent.fqn if self.parent else ""
        if hasattr(self.ast, "name"):
            node_name = str(self.ast.name)
            if parent_prefix:
                return f"{parent_prefix}.{node_name}"

            return node_name

        return parent_prefix

    def __str__(self) -> str:
        return ast_label(self.ast)

    def __repr__(self) -> str:
        return ast_dump(self.ast, short=True)

    @classmethod
    def _ordinal(cls) -> int:
        cls._ordinal_counter += 1
        return cls._ordinal_counter
