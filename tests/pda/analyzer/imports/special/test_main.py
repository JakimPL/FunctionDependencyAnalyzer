import ast
from dataclasses import dataclass
from typing import Tuple

import pytest

from pda.analyzer.imports.special.main import is_main_guard_only


class TestIfMainGuard:
    @dataclass
    class TestCase:
        __test__ = False

        label: str
        expected: Tuple[bool, ...]
        code: str

    test_cases = [
        TestCase(
            label="direct_main_guard",
            expected=(True,),
            code="""
if __name__ == "__main__":
    pass
            """,
        ),
        TestCase(
            label="direct_not_main_guard",
            expected=(False,),
            code="""
if __name__ != "__main__":
    pass
            """,
        ),
        TestCase(
            label="swapped_comparison",
            expected=(True,),
            code="""
if "__main__" == __name__:
    pass
            """,
        ),
        TestCase(
            label="indirect_not_main_guard",
            expected=(False,),
            code="""
if not __name__ == "__main__":
    pass
            """,
        ),
        TestCase(
            label="and_clause",
            expected=(True,),
            code="""
if some_condition and "__main__" == __name__:
    pass
            """,
        ),
        TestCase(
            label="or_clause",
            expected=(False,),
            code="""
if __name__ == "__main__" or another_condition:
    pass
""",
        ),
        TestCase(
            label="not_main_guard_in_elif",
            expected=(False, False, True),
            code="""
if not __name__ == "__main__":
    pass
elif some_condition:
    pass
else:
    pass
""",
        ),
        TestCase(
            label="main_guard_in_else",
            expected=(False, False, True),
            code="""
if __name__ == "__main__" or some_condition:
    pass
elif __name__ != "__main__":
    pass
else:
    pass
""",
        ),
    ]

    def _find_if_nodes(self, root: ast.Module) -> Tuple[ast.If, ...]:
        return tuple(node for node in root.body if isinstance(node, ast.If))

    @pytest.mark.parametrize("test_case", test_cases, ids=lambda tc: tc.label)
    def test_main_guard(self, test_case: TestCase) -> None:
        root = ast.parse(test_case.code)
        if_nodes = self._find_if_nodes(root)

        if not len(if_nodes) == 1:
            raise ValueError(f"Expected exactly 1 If node in test case, found {len(if_nodes)}")

        results = []
        if_node = if_nodes[0]
        current = if_node
        while current:
            results.append(is_main_guard_only(current, in_else_branch=False))

            if current.orelse:
                if len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If):
                    current = current.orelse[0]
                else:
                    results.append(is_main_guard_only(if_node, in_else_branch=True))
                    break
            else:
                break

        assert tuple(results) == test_case.expected, f"Expected: {test_case.expected}, got: {tuple(results)}"
