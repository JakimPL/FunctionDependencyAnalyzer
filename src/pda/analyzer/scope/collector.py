import ast
from typing import Any, Dict, List, Union

from pda.models import ASTForest, ASTNode
from pda.specification import SourceSpan, Symbol


class SymbolCollector:
    """
    Collects symbol definitions from an AST and returns them as data.

    This class walks the AST and extracts all definitions (assignments,
    function/class definitions, parameters, etc.) without needing scope objects.
    """

    def __init__(self) -> None:
        """
        Initialize the symbol collector.
        """
        self._forest: ASTForest | None = None
        self._symbols_by_node: Dict[ASTNode[Any], Dict[str, Symbol]] = {}
        self._node_to_scope_node: Dict[ASTNode[Any], ASTNode[Any]] = {}

    def __call__(
        self, forest: ASTForest, node_to_scope_node: Dict[ASTNode[Any], ASTNode[Any]]
    ) -> Dict[ASTNode[Any], Dict[str, Symbol]]:
        """
        Collect all symbols and return them mapped by scope-defining AST nodes.

        Args:
            forest: The ASTForest to collect symbols from.
            node_to_scope_node: Mapping from any AST node to its containing scope-defining node.

        Returns:
            Dictionary mapping scope-defining AST nodes to their symbols {name: Symbol}.
        """
        self._forest = forest
        self._node_to_scope_node = node_to_scope_node
        self._symbols_by_node = {}

        for root in forest.roots:
            self._collect_in_scope(root)

        return self._symbols_by_node

    def _collect_in_scope(
        self,
        scope_node: ASTNode[Any],
    ) -> None:
        """
        Collect symbols defined in a scope and recursively process child scopes.

        Args:
            scope_node: The scope-defining AST node to process.
        """
        if scope_node not in self._symbols_by_node:
            self._symbols_by_node[scope_node] = {}

        self._visit_scope_body(scope_node)

        # Find and process child scopes
        for child in scope_node.children:
            if self._is_scope_defining(child):
                self._collect_in_scope(child)

    def _is_scope_defining(self, node: ASTNode[Any]) -> bool:
        """Check if a node defines a new scope."""
        return isinstance(
            node.ast,
            (
                ast.Module,
                ast.ClassDef,
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.Lambda,
                ast.ListComp,
                ast.SetComp,
                ast.DictComp,
                ast.GeneratorExp,
            ),
        )

    def _visit_scope_body(
        self,
        scope_node: ASTNode[Any],
    ) -> None:
        """
        Visit the body of a scope (not the defining node itself).

        Args:
            scope_node: The scope-defining AST node.
        """
        for child in scope_node.children:
            self._visit_node(child, scope_node)

    def _visit_node(
        self,
        node: ASTNode[Any],
        scope_node: ASTNode[Any],
    ) -> None:
        """
        Visit a node and collect symbols it defines.

        Args:
            node: The ASTNode to visit.
            scope_node: The containing scope-defining node.
        """
        if self._is_scope_defining(node):
            return

        match node.ast:
            case ast.FunctionDef() | ast.AsyncFunctionDef():
                self._collect_function(node, scope_node)
            case ast.ClassDef():
                self._collect_class(node, scope_node)
            case ast.Assign() | ast.AugAssign() | ast.AnnAssign():
                self._collect_assignment(node, scope_node)
            case ast.NamedExpr():
                self._collect_walrus(node, scope_node)
            case ast.For() | ast.AsyncFor():
                self._collect_for_target(node, scope_node)
            case ast.With() | ast.AsyncWith():
                self._collect_with_targets(node, scope_node)
            case ast.ExceptHandler():
                self._collect_exception_handler(node, scope_node)
            case ast.Match():
                self._collect_match_targets(node, scope_node)
            case _:
                pass

        for child in node.children:
            if not self._is_scope_defining(child):
                self._visit_node(child, scope_node)

    def _collect_function(
        self,
        node: ASTNode[Union[ast.FunctionDef, ast.AsyncFunctionDef]],
        scope_node: ASTNode[Any],
    ) -> None:
        """
        Collect a function definition and its parameters.

        Args:
            node: The function definition node.
            scope_node: The scope where the function is defined (NOT the function's own scope).
        """
        func_def = node.ast
        self._define_symbol(func_def.name, func_def, scope_node, node)

        # Function parameters go in the function's own scope
        if node in self._symbols_by_node or self._is_scope_defining(node):
            if node not in self._symbols_by_node:
                self._symbols_by_node[node] = {}
            self._collect_parameters(func_def.args, node)

    def _collect_class(
        self,
        node: ASTNode[ast.ClassDef],
        scope_node: ASTNode[Any],
    ) -> None:
        """
        Collect a class definition.

        Args:
            node: The class definition node.
            scope_node: The scope where the class is defined.
        """
        self._define_symbol(node.ast.name, node.ast, scope_node, node)

    def _collect_assignment(
        self,
        node: ASTNode[Union[ast.Assign, ast.AugAssign, ast.AnnAssign]],
        scope_node: ASTNode[Any],
    ) -> None:
        """
        Collect assignment targets as symbols.

        Args:
            node: The assignment node.
            scope_node: The containing scope.
        """
        targets = self._get_assignment_targets(node.ast)
        for target in targets:
            self._collect_names_from_target(target, node.ast, scope_node, node)

    def _collect_walrus(
        self,
        node: ASTNode[ast.NamedExpr],
        scope_node: ASTNode[Any],
    ) -> None:
        """
        Collect walrus operator assignment target.

        Args:
            node: The named expression node.
            scope_node: The containing scope.
        """
        target = node.ast.target
        if isinstance(target, ast.Name):
            self._define_symbol(target.id, node.ast, scope_node, node)

    def _collect_for_target(
        self,
        node: ASTNode[Union[ast.For, ast.AsyncFor]],
        scope_node: ASTNode[Any],
    ) -> None:
        """
        Collect for loop target variables.

        Args:
            node: The for loop node.
            scope_node: The containing scope.
        """
        self._collect_names_from_target(node.ast.target, node.ast, scope_node, node)

    def _collect_with_targets(
        self,
        node: ASTNode[Union[ast.With, ast.AsyncWith]],
        scope_node: ASTNode[Any],
    ) -> None:
        """
        Collect with statement target variables.

        Args:
            node: The with statement node.
            scope_node: The containing scope.
        """
        for item in node.ast.items:
            if item.optional_vars is not None:
                self._collect_names_from_target(item.optional_vars, node.ast, scope_node, node)

    def _collect_exception_handler(
        self,
        node: ASTNode[ast.ExceptHandler],
        scope_node: ASTNode[Any],
    ) -> None:
        """
        Collect exception handler variable.

        Args:
            node: The exception handler node.
            scope_node: The containing scope.
        """
        if node.ast.name is not None:
            self._define_symbol(node.ast.name, node.ast, scope_node, node)

    def _collect_match_targets(
        self,
        node: ASTNode[ast.Match],
        scope_node: ASTNode[Any],
    ) -> None:
        """
        Collect pattern variables from match cases.

        Args:
            node: The match statement node.
            scope_node: The containing scope.
        """
        for case in node.ast.cases:
            self._collect_names_from_pattern(case.pattern, case, scope_node, node)

    def _collect_parameters(
        self,
        args: ast.arguments,
        scope_node: ASTNode[Any],
    ) -> None:
        """
        Collect function parameters as symbols.

        Args:
            args: The function arguments node.
            scope_node: The function's scope node.
        """
        all_args: List[ast.arg] = []

        if args.posonlyargs:
            all_args.extend(args.posonlyargs)
        if args.args:
            all_args.extend(args.args)
        if args.vararg:
            all_args.append(args.vararg)
        if args.kwonlyargs:
            all_args.extend(args.kwonlyargs)
        if args.kwarg:
            all_args.append(args.kwarg)

        for arg in all_args:
            self._define_symbol(arg.arg, arg, scope_node, scope_node)

    def _get_assignment_targets(self, node: Union[ast.Assign, ast.AugAssign, ast.AnnAssign]) -> List[ast.expr]:
        """
        Extract target expressions from an assignment node.

        Args:
            node: The assignment node.

        Returns:
            List of target expressions.
        """
        match node:
            case ast.Assign():
                return node.targets
            case ast.AugAssign():
                return [node.target]
            case ast.AnnAssign():
                return [node.target] if node.target else []
            case _:
                return []

    def _collect_names_from_target(
        self,
        target: ast.expr,
        def_node: ast.AST,
        scope_node: ASTNode[Any],
        ast_node: ASTNode[Any],
    ) -> None:
        """
        Recursively extract names from an assignment target.

        Handles: Name, Tuple, List (unpacking).

        Args:
            target: The target expression.
            def_node: The defining node (for creating Symbol).
            scope_node: The containing scope node.
            ast_node: The ASTNode for FQN calculation.
        """
        match target:
            case ast.Name():
                self._define_symbol(target.id, def_node, scope_node, ast_node)
            case ast.Tuple() | ast.List():
                for elt in target.elts:
                    self._collect_names_from_target(elt, def_node, scope_node, ast_node)
            case _:
                pass

    def _collect_names_from_pattern(
        self,
        pattern: ast.pattern,
        def_node: ast.AST,
        scope_node: ASTNode[Any],
        ast_node: ASTNode[Any],
    ) -> None:
        """
        Recursively extract names from a match pattern.

        Args:
            pattern: The pattern node.
            def_node: The defining node (case node).
            scope_node: The containing scope node.
            ast_node: The ASTNode for FQN calculation.
        """
        match pattern:
            case ast.MatchAs():
                if pattern.name is not None:
                    self._define_symbol(pattern.name, def_node, scope_node, ast_node)
                if pattern.pattern is not None:
                    self._collect_names_from_pattern(pattern.pattern, def_node, scope_node, ast_node)
            case ast.MatchOr():
                for subpattern in pattern.patterns:
                    self._collect_names_from_pattern(subpattern, def_node, scope_node, ast_node)
            case ast.MatchSequence():
                for subpattern in pattern.patterns:
                    self._collect_names_from_pattern(subpattern, def_node, scope_node, ast_node)
            case ast.MatchMapping():
                for subpattern in pattern.patterns:
                    self._collect_names_from_pattern(subpattern, def_node, scope_node, ast_node)
                if pattern.rest is not None:
                    self._define_symbol(pattern.rest, def_node, scope_node, ast_node)
            case ast.MatchClass():
                for subpattern in pattern.patterns:
                    self._collect_names_from_pattern(subpattern, def_node, scope_node, ast_node)
                for subpattern in pattern.kwd_patterns:
                    self._collect_names_from_pattern(subpattern, def_node, scope_node, ast_node)
            case ast.MatchStar():
                if pattern.name is not None:
                    self._define_symbol(pattern.name, def_node, scope_node, ast_node)
            case _:
                pass

    def _define_symbol(
        self,
        name: str,
        node: ast.AST,
        scope_node: ASTNode[Any],
        ast_node: ASTNode[Any],
    ) -> None:
        """
        Create a Symbol and add it to the dictionary.

        Args:
            name: The symbol name.
            node: The AST node defining this symbol.
            scope_node: The scope this symbol belongs to.
            ast_node: The ASTNode for calculating FQN prefix.
        """
        fqn_prefix = ast_node.fqn
        fqn = f"{fqn_prefix}.{name}" if fqn_prefix else name

        assert self._forest is not None, "Forest must be set before defining symbols"
        origin = self._forest.get_origin(ast_node)
        if origin is None:
            origin = self._forest.get_origin(scope_node)

        assert origin is not None, f"Cannot find origin for node {ast_node}"

        symbol = Symbol(
            node=node,
            fqn=fqn,
            origin=origin,
            span=SourceSpan.from_ast(node),
        )

        if scope_node not in self._symbols_by_node:
            self._symbols_by_node[scope_node] = {}

        self._symbols_by_node[scope_node][name] = symbol
