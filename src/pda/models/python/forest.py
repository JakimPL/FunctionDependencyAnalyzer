from __future__ import annotations

import ast
from pathlib import Path
from typing import Any, Optional

from pda.models.python.node import ASTNode
from pda.parser import parse_python_file
from pda.structures.forest.base import BaseForest


class ASTForest(BaseForest[Path, ast.AST, ASTNode[Any]]):
    """
    Wraps an AST as a anytree tree structure for convenient traversal and analysis.
    """

    def _build_tree(
        self,
        item: ast.AST,
        parent: Optional[ASTNode[Any]] = None,
    ) -> None:
        node = self._add_node(item, parent=parent)
        if node is None:
            return

        if parent is None:
            self._roots.add(node)

        for child in ast.iter_child_nodes(node.ast):
            self._build_tree(child, parent=node)

    def _create_node(
        self,
        item: ast.AST,
        parent: Optional[ASTNode[Any]] = None,
    ) -> ASTNode[Any]:
        return ASTNode[Any](item, parent=parent)

    def label(self, node: ASTNode[Any]) -> str:
        return node.name

    def item(self, node: ASTNode[Any]) -> ast.AST:
        ast_node: ast.AST = node.ast
        return ast_node

    def _input_to_item(self, inp: Path) -> ast.Module:
        return parse_python_file(inp)
