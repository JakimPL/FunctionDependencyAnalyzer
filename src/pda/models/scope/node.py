from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from pda.models.python.dump import ast_dump
from pda.models.python.node import ASTNode
from pda.specification import ScopeType, Symbol
from pda.structures import AnyNode
from pda.types import ASTT


class ScopeNode(AnyNode[ASTNode[ASTT]]):
    """
    Represents a Python scope with its symbol table.

    A scope tracks local definitions and imported symbols, and maintains
    a reference to its parent scope for hierarchical name resolution.
    """

    parent: Optional[ScopeNode[ASTT]]

    def __init__(
        self,
        scope_type: ScopeType,
        node: ASTNode[ASTT],
        origin: Path,
        *,
        parent: Optional[ScopeNode[ASTT]] = None,
        label: Optional[str] = None,
        symbols: Optional[Dict[str, Symbol]] = None,
        imports: Optional[Dict[str, Symbol]] = None,
    ) -> None:
        """
        Initialize a new scope.

        Args:
            scope_type: The type of this scope (MODULE, CLASS, FUNCTION, etc.).
            node: The AST node that created this scope.
            origin: The file path where this scope is defined.
            parent: The enclosing parent scope (None for module scope).
            label: The label for this scope node (if None, defaults to formatted scope label).
            symbols: Dictionary of symbols defined in this scope.
            imports: Dictionary of imported symbols in this scope.
        """
        label = label or node.label
        details = self._build_scope_details(scope_type, symbols, imports)
        group = node.group
        super().__init__(
            item=node,
            parent=parent,
            ordinal=id(node),
            label=label,
            details=details,
            group=group,
        )
        self.scope_type = scope_type
        self.origin = origin
        self.symbols = symbols or {}
        self.imports = imports or {}

    @property
    def node(self) -> ASTNode[ASTT]:
        """Get the AST node that created this scope."""
        return self.item

    def __repr__(self) -> str:
        """String representation for debugging."""
        node_info = ast_dump(self.node.ast)
        return f"Scope({self.scope_type.value}, {node_info}, {len(self.symbols)} symbols, {len(self.imports)} imports)"

    def lookup_local(self, name: str) -> Optional[Symbol]:
        """
        Look up a name only in this scope, without walking up the scope chain.

        Args:
            name: The name to look up.

        Returns:
            Symbol if found in this scope (checking both local definitions
            and imports), None otherwise.
        """
        if name in self.symbols:
            return self.symbols[name]

        if name in self.imports:
            return self.imports[name]

        return None

    def lookup(self, name: str) -> Optional[Symbol]:
        """
        Look up a name in this scope and walk up the scope chain if not found.

        This implements Python's LEGB rule (Local, Enclosing, Global, Built-in),
        but without built-ins. Note that class scopes are skipped when looking
        up from function scopes (Python semantics).

        Args:
            name: The name to look up.

        Returns:
            Symbol if found in this scope or any parent scope, None otherwise.
        """
        symbol = self.lookup_local(name)
        if symbol is not None:
            return symbol

        parent_scope = self.parent
        if parent_scope is not None:
            if self.scope_type == ScopeType.FUNCTION and parent_scope.scope_type == ScopeType.CLASS:
                grandparent_scope = parent_scope.parent
                if grandparent_scope is not None:
                    return grandparent_scope.lookup(name)

                return None

            return parent_scope.lookup(name)

        return None

    def lookup_nonlocal(self, name: str) -> Optional[Symbol]:
        """
        Look up a name for nonlocal/closure resolution, skipping module and class scopes.

        This is used for resolving names in nested functions where 'nonlocal'
        might be used. It skips module-level and class-level scopes.

        Args:
            name: The name to look up.

        Returns:
            Symbol if found in enclosing function scopes, None otherwise.
        """
        current: Optional[ScopeNode[Any]] = self.parent

        while current is not None:
            if current.scope_type in (ScopeType.MODULE, ScopeType.CLASS):
                current = current.parent
                continue

            symbol = current.lookup_local(name)
            if symbol is not None:
                return symbol

            current = current.parent

        return None

    @property
    def fqn(self) -> str:
        """
        Get the fully qualified name prefix for symbols defined in this scope.

        Delegates to the underlying ASTNode.

        Returns:
            String like "module.path.ClassName" or "module.path".
        """
        return self.node.fqn

    @staticmethod
    def _build_scope_details(
        scope_type: ScopeType,
        symbols: Optional[Dict[str, Symbol]],
        imports: Optional[Dict[str, Symbol]],
    ) -> str:
        """Build details string for scope node display."""
        symbol_count = len(symbols or {})
        import_count = len(imports or {})
        return f"{scope_type.value} | {symbol_count} symbols | {import_count} imports"
