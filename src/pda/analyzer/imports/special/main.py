import ast
from typing import Optional, cast


def is_main_guard_only(if_node: ast.If, in_else_branch: bool = False) -> bool:
    if in_else_branch:
        return _any_branch_excludes_main_guard(if_node)

    test = if_node.test

    if isinstance(test, ast.Compare) and _is_main_guard_comparison(test):
        return True

    if _is_and_clause(test):
        return _contains_main_guard_in_and(test)

    if _is_or_clause(test):
        return False

    return False


def _is_name_dunder_name(node: ast.expr) -> bool:
    return isinstance(node, ast.Name) and node.id == "__name__"


def _is_main_string(node: ast.expr) -> bool:
    return isinstance(node, ast.Constant) and node.value == "__main__"


def _is_main_guard_comparison(node: ast.Compare) -> bool:
    if len(node.ops) != 1 or len(node.comparators) != 1:
        return False

    op = node.ops[0]
    if not isinstance(op, ast.Eq):
        return False

    left_is_name = _is_name_dunder_name(node.left)
    right_is_main = _is_main_string(node.comparators[0])

    left_is_main = _is_main_string(node.left)
    right_is_name = _is_name_dunder_name(node.comparators[0])

    return (left_is_name and right_is_main) or (left_is_main and right_is_name)


def _contains_main_guard_in_and_chain(node: ast.BoolOp) -> bool:
    for value in node.values:
        if isinstance(value, ast.Compare) and _is_main_guard_comparison(value):
            return True

    return False


def _contains_main_guard_in_and(node: ast.expr) -> bool:
    if isinstance(node, ast.Compare):
        return _is_main_guard_comparison(node)

    if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
        return _contains_main_guard_in_and_chain(node)

    return False


def _is_negated_main_guard_comparison(node: ast.Compare) -> bool:
    if len(node.ops) != 1 or len(node.comparators) != 1:
        return False

    op = node.ops[0]
    if not isinstance(op, ast.NotEq):
        return False

    left_is_name = _is_name_dunder_name(node.left)
    right_is_main = _is_main_string(node.comparators[0])

    left_is_main = _is_main_string(node.left)
    right_is_name = _is_name_dunder_name(node.comparators[0])

    return (left_is_name and right_is_main) or (left_is_main and right_is_name)


def _is_negated_main_guard(node: ast.expr) -> bool:
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        if isinstance(node.operand, ast.Compare):
            return _is_main_guard_comparison(node.operand)

    if isinstance(node, ast.Compare):
        return _is_negated_main_guard_comparison(node)

    return False


def _contains_negated_main_guard_in_or_chain(node: ast.BoolOp) -> bool:
    for value in node.values:
        if _is_negated_main_guard(value):
            return True

    return False


def _contains_main_guard_negation(node: ast.expr) -> bool:
    if _is_negated_main_guard(node):
        return True

    if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
        return _contains_negated_main_guard_in_or_chain(node)

    return False


def _is_elif_branch(orelse: list[ast.stmt]) -> bool:
    return len(orelse) == 1 and isinstance(orelse[0], ast.If)


def _get_next_elif(current: ast.If) -> Optional[ast.If]:
    if current.orelse and _is_elif_branch(current.orelse):
        return cast(ast.If, current.orelse[0])

    return None


def _any_branch_excludes_main_guard(if_node: ast.If) -> bool:
    current: Optional[ast.If] = if_node

    while current:
        if _contains_main_guard_negation(current.test):
            return True
        current = _get_next_elif(current)

    return False


def _is_or_clause(node: ast.expr) -> bool:
    return isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or)


def _is_and_clause(node: ast.expr) -> bool:
    return isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And)
