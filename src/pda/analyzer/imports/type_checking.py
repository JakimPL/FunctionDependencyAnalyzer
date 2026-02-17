import ast
from typing import Any, Optional


def is_type_checking_name(node: ast.expr) -> bool:
    return isinstance(node, ast.Name) and node.id == "TYPE_CHECKING"


def is_bool_type_checking_call(node: ast.expr) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "bool"
        and len(node.args) == 1
        and is_type_checking_name(node.args[0])
    )


def is_type_checking_reference(node: ast.expr) -> bool:
    return is_type_checking_name(node) or is_bool_type_checking_call(node)


def _simplify_type_checking_comparison(op: ast.cmpop, comparator: ast.expr) -> Optional[bool]:
    if not isinstance(comparator, ast.Constant):
        return None

    if isinstance(op, (ast.Eq, ast.Is)):
        if comparator.value is True:
            return True
        if comparator.value is False:
            return False

    if isinstance(op, (ast.NotEq, ast.IsNot)):
        if comparator.value is False:
            return True
        if comparator.value is True:
            return False

    if isinstance(op, ast.Gt) and comparator.value == 0:
        return True

    if isinstance(op, ast.Lt) and comparator.value == 1:
        return False

    return None


def _evaluate_constant_comparison(left_val: Any, op: ast.cmpop, right_val: Any) -> Optional[bool]:
    comparison: Optional[bool] = None
    try:
        match op:
            case ast.Gt():
                comparison = left_val > right_val
            case ast.Lt():
                comparison = left_val < right_val
            case ast.Eq():
                comparison = left_val == right_val
            case ast.NotEq():
                comparison = left_val != right_val
            case ast.GtE():
                comparison = left_val >= right_val
            case ast.LtE():
                comparison = left_val <= right_val

    except TypeError:
        return None

    return comparison


def simplify_comparison(node: ast.expr) -> Optional[bool]:
    if isinstance(node, ast.Constant):
        return bool(node.value)

    if isinstance(node, ast.Compare):
        if is_type_checking_reference(node.left) and len(node.ops) == 1 and len(node.comparators) == 1:
            return _simplify_type_checking_comparison(node.ops[0], node.comparators[0])

        if isinstance(node.left, ast.Constant) and len(node.ops) == 1 and isinstance(node.comparators[0], ast.Constant):
            return _evaluate_constant_comparison(node.left.value, node.ops[0], node.comparators[0].value)

    if is_bool_type_checking_call(node):
        return True

    return None


def contains_type_checking_in_and(node: ast.expr) -> bool:
    if is_type_checking_name(node):
        return True

    if isinstance(node, ast.Compare):
        result = simplify_comparison(node)
        if result is True:
            return is_type_checking_reference(node.left)
        return False

    if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
        has_type_checking = False
        for value in node.values:
            if is_type_checking_name(value):
                has_type_checking = True
            
            elif isinstance(value, ast.Compare):
                if simplify_comparison(value) is True and is_type_checking_reference(value.left):
                    has_type_checking = True
        
        return has_type_checking

    return False


def can_simplify_to_true(node: ast.expr) -> bool:
    result = simplify_comparison(node)
    return result is True


def contains_type_checking_negation(node: ast.expr) -> bool:
    """
    Check if a condition contains TYPE_CHECKING in a way that makes it False when TYPE_CHECKING is True.
    Examples:
    - not TYPE_CHECKING → True (negation)
    - not TYPE_CHECKING or something → True (in OR with negation)
    """
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return is_type_checking_name(node.operand)

    if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
        for value in node.values:
            if isinstance(value, ast.UnaryOp) and isinstance(value.op, ast.Not):
                if is_type_checking_name(value.operand):
                    return True

    return False


def any_branch_excludes_type_checking(if_node: ast.If) -> bool:
    """
    Check if any if/elif branch is guaranteed True when TYPE_CHECKING is False.
    This means the else branch would only execute when TYPE_CHECKING is True.

    For example:
    - if some_condition: pass
    - elif not TYPE_CHECKING or another: pass
    - else: import  # type-checking only

    The elif is always True when TYPE_CHECKING is False, so else can only run when TYPE_CHECKING is True.
    """
    current = if_node

    while current:
        test = current.test

        if contains_type_checking_negation(test):
            return True

        if current.orelse and len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If):
            current = current.orelse[0]
        else:
            break

    return False


def is_type_checking_only(if_node: ast.If, in_else_branch: bool = False) -> bool:
    """
    Determine if an import in this If node is type-checking only.
    """
    if in_else_branch:
        return any_branch_excludes_type_checking(if_node)

    test = if_node.test

    if is_type_checking_name(test):
        return True

    simplified = simplify_comparison(test)
    if simplified is True:
        return contains_type_checking_in_and(test)

    if isinstance(test, ast.BoolOp) and isinstance(test.op, ast.And):
        return contains_type_checking_in_and(test)

    if isinstance(test, ast.BoolOp) and isinstance(test.op, ast.Or):
        return False

    return False
