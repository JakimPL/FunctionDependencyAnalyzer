from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional

import pytest

from pda.analyzer.scope import ScopeAnalyzer
from pda.models.scope import ScopeNode
from pda.specification import ScopeType


@dataclass
class ScopeExpectation:
    """Expected properties of a scope."""

    path: List[str]
    type: ScopeType
    symbol_count: int
    parent_path: Optional[List[str]] = None


@dataclass
class SymbolExpectation:
    """Expected properties of a symbol."""

    name: str
    scope_path: List[str]
    fqn: str
    origin_file: str


class ScopeAnalysisTestBase(ABC):
    """Base class for scope analysis tests with common infrastructure."""

    scope_expectations: List[ScopeExpectation] = []
    symbol_expectations: List[SymbolExpectation] = []

    @pytest.fixture
    @abstractmethod
    def module_scope(self) -> ScopeNode[Any]: ...

    def analyze_file(self, filepath: Path) -> ScopeNode[Any]:
        """
        Analyze a single file and return its module scope.

        Args:
            filepath: Path to the file to analyze.

        Returns:
            The root (module) scope node.
        """
        analyzer = ScopeAnalyzer()
        scope_forest = analyzer([filepath])
        roots = list(scope_forest.roots)
        assert len(roots) == 1, f"Expected 1 root, got {len(roots)}"
        return roots[0]

    def find_scope(self, root: ScopeNode[Any], path: List[str]) -> ScopeNode[Any]:
        """
        Find a scope by following a path from the root.

        The path is a list of scope name segments. For example:
        - [] finds the root (module) scope
        - ["my_function"] finds a function in the module
        - ["MyClass", "my_method"] finds a method in a class

        Args:
            root: The root scope to start searching from.
            path: List of scope name segments to follow.

        Returns:
            The scope node at the end of the path.

        Raises:
            AssertionError: If any segment in the path cannot be found.
        """
        current_scope = root

        for segment in path:
            found_child = None
            child: ScopeNode[Any]
            for child in current_scope.children:
                if segment in child.label:
                    found_child = child
                    break

            assert found_child is not None, (
                f"Could not find scope '{segment}' in path {path}. "
                f"Available children: {[child.label for child in current_scope.children]}"
            )
            current_scope = found_child

        return current_scope

    def assert_scope_structure(self, root: ScopeNode[Any], expectation: ScopeExpectation) -> ScopeNode[Any]:
        """
        Assert that a scope has the expected structure.

        Validates:
        - Scope exists at the given path
        - Scope has the correct type
        - Scope has the expected number of symbols
        - Scope has the correct parent

        Args:
            root: The root scope to search from.
            expectation: The expected scope properties.

        Returns:
            The validated scope node.

        Raises:
            AssertionError: If any validation fails.
        """
        scope = self.find_scope(root, expectation.path)

        assert scope.scope_type == expectation.type, (
            f"Scope at {expectation.path}: " f"expected type {expectation.type.value}, got {scope.scope_type.value}"
        )

        actual_symbol_count = len(scope.symbols)
        if actual_symbol_count != expectation.symbol_count:
            child_info = "\n".join(
                f"  - {child.label}: {child.scope_type.value} with {len(child.symbols)} symbols: {list(child.symbols.keys())}"
                for child in scope.children
            )
            assert False, (
                f"Scope at {expectation.path}: "
                f"expected {expectation.symbol_count} symbols, got {actual_symbol_count}.\n"
                f"Actual symbols: {list(scope.symbols.keys())}\n"
                f"Child scopes ({len(list(scope.children))}):\n{child_info if child_info else '  (none)'}"
            )

        if expectation.parent_path is None:
            assert scope.parent is None, f"Scope at {expectation.path}: expected no parent, but has one"
        else:
            assert scope.parent is not None, f"Scope at {expectation.path}: expected parent, but has none"
            expected_parent = self.find_scope(root, expectation.parent_path)
            assert scope.parent == expected_parent, (
                f"Scope at {expectation.path}: parent mismatch. " f"Expected parent at {expectation.parent_path}"
            )

        return scope

    def assert_symbol_properties(self, root: ScopeNode[Any], expectation: SymbolExpectation) -> None:
        """
        Assert that a symbol has the expected properties.

        Validates:
        - Symbol exists in the specified scope
        - Symbol has the correct FQN
        - Symbol has the correct origin file
        - Symbol has required metadata (node, span)

        Args:
            root: The root scope to search from.
            expectation: The expected symbol properties.

        Raises:
            AssertionError: If any validation fails.
        """
        scope = self.find_scope(root, expectation.scope_path)

        assert expectation.name in scope.symbols, (
            f"Symbol '{expectation.name}' not found in scope at {expectation.scope_path}. "
            f"Available symbols: {list(scope.symbols.keys())}"
        )

        symbol = scope.symbols[expectation.name]

        assert symbol.fqn == expectation.fqn, (
            f"Symbol '{expectation.name}' at {expectation.scope_path}: "
            f"expected FQN '{expectation.fqn}', got '{symbol.fqn}'"
        )

        assert symbol.origin is not None, f"Symbol '{expectation.name}': missing origin"
        assert symbol.origin.name == expectation.origin_file, (
            f"Symbol '{expectation.name}': " f"expected origin '{expectation.origin_file}', got '{symbol.origin.name}'"
        )

        assert symbol.node is not None, f"Symbol '{expectation.name}': missing AST node"
        assert symbol.span is not None, f"Symbol '{expectation.name}': missing source span"
        assert symbol.span.lineno > 0, f"Symbol '{expectation.name}': invalid lineno"
        assert symbol.span.col_offset >= 0, f"Symbol '{expectation.name}': invalid col_offset"

    def validate_complete_analysis(
        self,
        root: ScopeNode[Any],
        scope_expectations: List[ScopeExpectation],
        symbol_expectations: List[SymbolExpectation],
    ) -> None:
        """
        Validate a complete scope analysis against expectations.

        This is the main entry point for tests. It validates:
        1. All expected scopes exist with correct structure
        2. All expected symbols exist with correct properties

        Args:
            root: The root scope from analysis.
            scope_expectations: List of all expected scopes.
            symbol_expectations: List of all expected symbols.

        Raises:
            AssertionError: If any validation fails.
        """
        for scope_exp in scope_expectations:
            self.assert_scope_structure(root, scope_exp)

        for symbol_exp in symbol_expectations:
            self.assert_symbol_properties(root, symbol_exp)
