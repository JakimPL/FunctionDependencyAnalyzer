from __future__ import annotations

import ast
from functools import cached_property
from typing import Any, Generic, Optional, Type, TypeVar

from pda.structures.node.base import BaseNode

NodeT = TypeVar("NodeT", bound=ast.AST)


class ASTNode(BaseNode[NodeT], Generic[NodeT]):
    def __init__(
        self,
        node: NodeT,
        parent: Optional[ASTNode[Any]] = None,
    ) -> None:
        super().__init__(item=node, parent=parent)
        self.ast: NodeT = node
        self.type: Type[NodeT] = type(node)

    @cached_property
    def name(self) -> str:
        return str(ast.dump(self.ast))
