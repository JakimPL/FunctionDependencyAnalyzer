import ast
from pathlib import Path
from typing import Any, List, Union

from anytree import PreOrderIter

from pda.models import ASTForest, ASTNode
from pda.specification import ImportPath, ImportScope, ImportStatement, SourceSpan


class ImportStatementParser:
    def __call__(self, origin: Path) -> List[ImportStatement]:
        tree = ASTForest([origin])
        import_nodes = self._find_import_nodes(tree)
        return self._retrieve_all_import_statements(origin, import_nodes)

    def _find_import_nodes(
        self,
        tree: ASTForest,
    ) -> List[ASTNode[Union[ast.Import, ast.ImportFrom]]]:
        return [node for node in tree.roots for node in PreOrderIter(node) if node.type in (ast.Import, ast.ImportFrom)]

    def _retrieve_all_import_statements(
        self,
        origin: Path,
        import_nodes: List[ASTNode[Union[ast.Import, ast.ImportFrom]]],
    ) -> List[ImportStatement]:
        statements: List[ImportStatement] = []
        for import_node in import_nodes:
            import_statements = self._create_import_statements(import_node, origin)
            statements.extend(import_statements)

        return statements

    def _create_import_statements(
        self,
        import_node: ASTNode[Union[ast.Import, ast.ImportFrom]],
        origin: Path,
    ) -> List[ImportStatement]:
        import_paths = ImportPath.from_ast(import_node.ast)
        span = SourceSpan.from_ast(import_node.ast)
        scope = self._determine_scope(import_node)

        return [
            ImportStatement(
                origin=origin,
                span=span,
                path=import_path,
                scope=scope,
            )
            for import_path in import_paths
        ]

    def _determine_scope(self, node: ASTNode[Any]) -> ImportScope:
        scope = ImportScope.NONE
        current = node.parent

        while current is not None:
            if not isinstance(current, ASTNode):
                current = current.parent
                continue

            match current.ast:
                case ast.If():
                    scope |= self._handle_if_scope(node, current.ast)
                case ast.Try():
                    scope |= self._handle_try_scope(node, current.ast)
                case ast.Match():
                    scope |= self._handle_match_scope(node, current.ast)
                case ast.For() | ast.While() | ast.ListComp() | ast.SetComp() | ast.DictComp() | ast.GeneratorExp():
                    scope |= ImportScope.LOOP
                case ast.With():
                    scope |= ImportScope.WITH
                case ast.FunctionDef() | ast.AsyncFunctionDef():
                    scope |= self._handle_function_scope(node, current.ast)
                case ast.ClassDef():
                    scope |= ImportScope.CLASS

            current = current.parent

        scope.validate()
        return scope

    def _handle_if_scope(self, node: ASTNode[Any], if_ast: ast.If) -> ImportScope:
        scope = ImportScope.NONE
        is_in_body = node.has_ancestor_of_id(if_ast.body)
        is_in_orelse = node.has_ancestor_of_id(if_ast.orelse)

        if is_in_body:
            scope |= ImportScope.IF
            if self._is_type_checking_condition(if_ast.test, negated=False):
                scope |= ImportScope.TYPE_CHECKING
            elif self._is_main_condition(if_ast.test):
                scope |= ImportScope.MAIN
        elif is_in_orelse:
            scope |= ImportScope.ELSE
            if self._is_type_checking_condition(if_ast.test, negated=True):
                scope |= ImportScope.TYPE_CHECKING

        if not is_in_body and not is_in_orelse:
            raise ValueError("Import node is child of If but not in body or orelse")

        return scope

    def _handle_try_scope(self, node: ASTNode[Any], try_ast: ast.Try) -> ImportScope:
        if try_ast.finalbody and node.has_ancestor_of_id(try_ast.finalbody):
            return ImportScope.FINALLY

        if try_ast.handlers:
            for handler in try_ast.handlers:
                if node.has_ancestor_of_id(handler.body):
                    return ImportScope.EXCEPT

        if try_ast.orelse and node.has_ancestor_of_id(try_ast.orelse):
            return ImportScope.TRY_ELSE

        if try_ast.body and node.has_ancestor_of_id(try_ast.body):
            return ImportScope.TRY

        raise ValueError("Import node is child of Try but not in any of its blocks")

    def _handle_match_scope(self, node: ASTNode[Any], match_ast: ast.Match) -> ImportScope:
        for case in match_ast.cases:
            if node.has_ancestor_of_id(case.body):
                if isinstance(case.pattern, ast.MatchAs) and case.pattern.pattern is None:
                    return ImportScope.DEFAULT
                return ImportScope.CASE
        return ImportScope.NONE

    def _handle_function_scope(
        self,
        node: ASTNode[Any],
        func_ast: Union[ast.FunctionDef, ast.AsyncFunctionDef],
    ) -> ImportScope:
        scope = ImportScope.FUNCTION
        if node.has_ancestor_of_id(func_ast.decorator_list):
            scope |= ImportScope.DECORATOR

        return scope

    def _is_type_checking_condition(self, test: ast.expr, negated: bool = False) -> bool:
        if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
            return negated and self._references_type_checking(test.operand)

        return not negated and self._references_type_checking(test)

    def _references_type_checking(self, node: ast.expr) -> bool:
        if isinstance(node, ast.Name) and node.id == "TYPE_CHECKING":
            return True

        if isinstance(node, ast.Attribute) and node.attr == "TYPE_CHECKING":
            return True

        if isinstance(node, ast.BoolOp):
            return any(self._references_type_checking(value) for value in node.values)

        return False

    def _is_main_condition(self, test: ast.expr) -> bool:
        return self._checks_name_main(test)

    def _checks_name_main(self, node: ast.expr) -> bool:
        if isinstance(node, ast.Compare):
            left_is_name = isinstance(node.left, ast.Name) and node.left.id == "__name__"
            right_is_main = any(
                isinstance(comp, ast.Constant) and comp.value == "__main__" for comp in node.comparators
            )
            return left_is_name and right_is_main

        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return self._checks_name_main(node.operand)

        if isinstance(node, ast.BoolOp):
            return any(self._checks_name_main(value) for value in node.values)

        return False
