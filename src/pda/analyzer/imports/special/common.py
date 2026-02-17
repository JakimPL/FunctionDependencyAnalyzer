import ast
from typing import Optional, cast


def is_elif_branch(orelse: list[ast.stmt]) -> bool:
    return len(orelse) == 1 and isinstance(orelse[0], ast.If)


def get_next_elif(current: ast.If) -> Optional[ast.If]:
    if current.orelse and is_elif_branch(current.orelse):
        return cast(ast.If, current.orelse[0])

    return None


def is_or_clause(node: ast.expr) -> bool:
    return isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or)


def is_and_clause(node: ast.expr) -> bool:
    return isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And)
