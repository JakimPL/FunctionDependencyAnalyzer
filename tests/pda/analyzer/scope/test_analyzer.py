from pathlib import Path
from typing import Any

import pytest

from pda.models.scope import ScopeNode
from pda.specification import ScopeType
from tests.pda.analyzer.scope.base import ScopeAnalysisTestBase, ScopeExpectation, SymbolExpectation


class TestAssignmentsFile(ScopeAnalysisTestBase):
    """Tests for tests/examples/scope/assignments.py"""

    scope_expectations = [
        ScopeExpectation(path=[], type=ScopeType.MODULE, symbol_count=34, parent_path=None),
        ScopeExpectation(
            path=["assignment_variations"],
            type=ScopeType.FUNCTION,
            symbol_count=14,
            parent_path=[],
        ),
        ScopeExpectation(
            path=["augmented_assignment_examples"],
            type=ScopeType.FUNCTION,
            symbol_count=1,
            parent_path=[],
        ),
        ScopeExpectation(
            path=["multiple_assignment_targets"],
            type=ScopeType.FUNCTION,
            symbol_count=7,
            parent_path=[],
        ),
        ScopeExpectation(
            path=["starred_expressions"],
            type=ScopeType.FUNCTION,
            symbol_count=9,
            parent_path=[],
        ),
        ScopeExpectation(
            path=["dictionary_unpacking"],
            type=ScopeType.FUNCTION,
            symbol_count=4,
            parent_path=[],
        ),
        ScopeExpectation(
            path=["tuple_unpacking_in_loop"],
            type=ScopeType.FUNCTION,
            symbol_count=6,
            parent_path=[],
        ),
        ScopeExpectation(
            path=["nested_dictionary_structure"],
            type=ScopeType.FUNCTION,
            symbol_count=4,
            parent_path=[],
        ),
        ScopeExpectation(
            path=["function_with_annotations"],
            type=ScopeType.FUNCTION,
            symbol_count=5,
            parent_path=[],
        ),
        ScopeExpectation(
            path=["function_with_annotations", "annotated_nested"],
            type=ScopeType.FUNCTION,
            symbol_count=2,
            parent_path=["function_with_annotations"],
        ),
        ScopeExpectation(
            path=["default_arguments_with_mutable"],
            type=ScopeType.FUNCTION,
            symbol_count=4,
            parent_path=[],
        ),
    ]

    symbol_expectations = [
        SymbolExpectation("x", [], "x", "assignments.py"),
        SymbolExpectation("y", [], "y", "assignments.py"),
        SymbolExpectation("z", [], "z", "assignments.py"),
        SymbolExpectation("a", [], "a", "assignments.py"),
        SymbolExpectation("b", [], "b", "assignments.py"),
        SymbolExpectation("c", [], "c", "assignments.py"),
        SymbolExpectation("nested_unpack", [], "nested_unpack", "assignments.py"),
        SymbolExpectation("d", [], "d", "assignments.py"),
        SymbolExpectation("e", [], "e", "assignments.py"),
        SymbolExpectation("f", [], "f", "assignments.py"),
        SymbolExpectation("dict_unpack", [], "dict_unpack", "assignments.py"),
        SymbolExpectation("key1", [], "key1", "assignments.py"),
        SymbolExpectation("key2", [], "key2", "assignments.py"),
        SymbolExpectation("key3", [], "key3", "assignments.py"),
        SymbolExpectation("dict_for_items", [], "dict_for_items", "assignments.py"),
        SymbolExpectation("first_key", [], "first_key", "assignments.py"),
        SymbolExpectation("first_value", [], "first_value", "assignments.py"),
        SymbolExpectation("remaining_items", [], "remaining_items", "assignments.py"),
        SymbolExpectation("module_variable", [], "module_variable", "assignments.py"),
        SymbolExpectation("annotated_variable", [], "annotated_variable", "assignments.py"),
        SymbolExpectation("assignment_variations", [], "assignment_variations", "assignments.py"),
        SymbolExpectation("augmented_assignment_examples", [], "augmented_assignment_examples", "assignments.py"),
        SymbolExpectation("multiple_assignment_targets", [], "multiple_assignment_targets", "assignments.py"),
        SymbolExpectation("starred_expressions", [], "starred_expressions", "assignments.py"),
        SymbolExpectation("dictionary_unpacking", [], "dictionary_unpacking", "assignments.py"),
        SymbolExpectation("tuple_unpacking_in_loop", [], "tuple_unpacking_in_loop", "assignments.py"),
        SymbolExpectation("nested_dictionary_structure", [], "nested_dictionary_structure", "assignments.py"),
        SymbolExpectation("function_with_annotations", [], "function_with_annotations", "assignments.py"),
        SymbolExpectation("default_arguments_with_mutable", [], "default_arguments_with_mutable", "assignments.py"),
        SymbolExpectation(
            "single_assign", ["assignment_variations"], "assignment_variations.single_assign", "assignments.py"
        ),
        SymbolExpectation(
            "multi_target", ["assignment_variations"], "assignment_variations.multi_target", "assignments.py"
        ),
        SymbolExpectation(
            "another_target", ["assignment_variations"], "assignment_variations.another_target", "assignments.py"
        ),
        SymbolExpectation("x", ["assignment_variations"], "assignment_variations.x", "assignments.py"),
        SymbolExpectation("y", ["assignment_variations"], "assignment_variations.y", "assignments.py"),
        SymbolExpectation("list_x", ["assignment_variations"], "assignment_variations.list_x", "assignments.py"),
        SymbolExpectation("list_y", ["assignment_variations"], "assignment_variations.list_y", "assignments.py"),
        SymbolExpectation("nested_a", ["assignment_variations"], "assignment_variations.nested_a", "assignments.py"),
        SymbolExpectation("nested_b", ["assignment_variations"], "assignment_variations.nested_b", "assignments.py"),
        SymbolExpectation("nested_c", ["assignment_variations"], "assignment_variations.nested_c", "assignments.py"),
        SymbolExpectation(
            "complex_dict", ["assignment_variations"], "assignment_variations.complex_dict", "assignments.py"
        ),
        SymbolExpectation("dict_key", ["assignment_variations"], "assignment_variations.dict_key", "assignments.py"),
        SymbolExpectation(
            "dict_values", ["assignment_variations"], "assignment_variations.dict_values", "assignments.py"
        ),
        SymbolExpectation(
            "remaining_dict_items",
            ["assignment_variations"],
            "assignment_variations.remaining_dict_items",
            "assignments.py",
        ),
        SymbolExpectation(
            "counter", ["augmented_assignment_examples"], "augmented_assignment_examples.counter", "assignments.py"
        ),
        SymbolExpectation("a", ["multiple_assignment_targets"], "multiple_assignment_targets.a", "assignments.py"),
        SymbolExpectation("b", ["multiple_assignment_targets"], "multiple_assignment_targets.b", "assignments.py"),
        SymbolExpectation("c", ["multiple_assignment_targets"], "multiple_assignment_targets.c", "assignments.py"),
        SymbolExpectation("x", ["multiple_assignment_targets"], "multiple_assignment_targets.x", "assignments.py"),
        SymbolExpectation("y", ["multiple_assignment_targets"], "multiple_assignment_targets.y", "assignments.py"),
        SymbolExpectation("z", ["multiple_assignment_targets"], "multiple_assignment_targets.z", "assignments.py"),
        SymbolExpectation(
            "temp_list", ["multiple_assignment_targets"], "multiple_assignment_targets.temp_list", "assignments.py"
        ),
        SymbolExpectation("first_item", ["starred_expressions"], "starred_expressions.first_item", "assignments.py"),
        SymbolExpectation("last_item", ["starred_expressions"], "starred_expressions.last_item", "assignments.py"),
        SymbolExpectation("end_item", ["starred_expressions"], "starred_expressions.end_item", "assignments.py"),
        SymbolExpectation("dict_data", ["starred_expressions"], "starred_expressions.dict_data", "assignments.py"),
        SymbolExpectation("first_key", ["starred_expressions"], "starred_expressions.first_key", "assignments.py"),
        SymbolExpectation("first_value", ["starred_expressions"], "starred_expressions.first_value", "assignments.py"),
        SymbolExpectation("dict1", ["dictionary_unpacking"], "dictionary_unpacking.dict1", "assignments.py"),
        SymbolExpectation("dict2", ["dictionary_unpacking"], "dictionary_unpacking.dict2", "assignments.py"),
        SymbolExpectation(
            "merged_dict", ["dictionary_unpacking"], "dictionary_unpacking.merged_dict", "assignments.py"
        ),
        SymbolExpectation(
            "dict_with_updates",
            ["dictionary_unpacking"],
            "dictionary_unpacking.dict_with_updates",
            "assignments.py",
        ),
        SymbolExpectation("data", ["tuple_unpacking_in_loop"], "tuple_unpacking_in_loop.data", "assignments.py"),
        SymbolExpectation(
            "person_dict", ["tuple_unpacking_in_loop"], "tuple_unpacking_in_loop.person_dict", "assignments.py"
        ),
        SymbolExpectation("name", ["tuple_unpacking_in_loop"], "tuple_unpacking_in_loop.name", "assignments.py"),
        SymbolExpectation("age", ["tuple_unpacking_in_loop"], "tuple_unpacking_in_loop.age", "assignments.py"),
        SymbolExpectation(
            "person_name", ["tuple_unpacking_in_loop"], "tuple_unpacking_in_loop.person_name", "assignments.py"
        ),
        SymbolExpectation(
            "person_age", ["tuple_unpacking_in_loop"], "tuple_unpacking_in_loop.person_age", "assignments.py"
        ),
        SymbolExpectation(
            "nested_dict",
            ["nested_dictionary_structure"],
            "nested_dictionary_structure.nested_dict",
            "assignments.py",
        ),
        SymbolExpectation(
            "outer_value",
            ["nested_dictionary_structure"],
            "nested_dictionary_structure.outer_value",
            "assignments.py",
        ),
        SymbolExpectation(
            "inner1", ["nested_dictionary_structure"], "nested_dictionary_structure.inner1", "assignments.py"
        ),
        SymbolExpectation(
            "inner2", ["nested_dictionary_structure"], "nested_dictionary_structure.inner2", "assignments.py"
        ),
        SymbolExpectation(
            "annotated_local",
            ["function_with_annotations"],
            "function_with_annotations.annotated_local",
            "assignments.py",
        ),
        SymbolExpectation(
            "annotated_integer",
            ["function_with_annotations"],
            "function_with_annotations.annotated_integer",
            "assignments.py",
        ),
        SymbolExpectation(
            "annotated_list",
            ["function_with_annotations"],
            "function_with_annotations.annotated_list",
            "assignments.py",
        ),
        SymbolExpectation(
            "annotated_dict",
            ["function_with_annotations"],
            "function_with_annotations.annotated_dict",
            "assignments.py",
        ),
        SymbolExpectation(
            "annotated_nested",
            ["function_with_annotations"],
            "function_with_annotations.annotated_nested",
            "assignments.py",
        ),
        SymbolExpectation(
            "parameter",
            ["function_with_annotations", "annotated_nested"],
            "function_with_annotations.annotated_nested.parameter",
            "assignments.py",
        ),
        SymbolExpectation(
            "result",
            ["function_with_annotations", "annotated_nested"],
            "function_with_annotations.annotated_nested.result",
            "assignments.py",
        ),
        SymbolExpectation(
            "mutable_default",
            ["default_arguments_with_mutable"],
            "default_arguments_with_mutable.mutable_default",
            "assignments.py",
        ),
        SymbolExpectation(
            "dict_default",
            ["default_arguments_with_mutable"],
            "default_arguments_with_mutable.dict_default",
            "assignments.py",
        ),
        SymbolExpectation(
            "local_list",
            ["default_arguments_with_mutable"],
            "default_arguments_with_mutable.local_list",
            "assignments.py",
        ),
        SymbolExpectation(
            "local_dict",
            ["default_arguments_with_mutable"],
            "default_arguments_with_mutable.local_dict",
            "assignments.py",
        ),
    ]

    @pytest.fixture
    def module_scope(self) -> ScopeNode[Any]:
        filepath = Path("tests/examples/scope/assignments.py")
        return self.analyze_file(filepath)

    def test_complete_scope_and_symbol_analysis(self, module_scope: ScopeNode[Any]) -> None:
        self.validate_complete_analysis(module_scope, self.scope_expectations, self.symbol_expectations)


class TestExceptionsFile(ScopeAnalysisTestBase):
    """Tests for tests/examples/scope/exceptions.py"""

    scope_expectations = [
        ScopeExpectation(path=[], type=ScopeType.MODULE, symbol_count=13, parent_path=None),
        ScopeExpectation(
            path=["basic_exception_handling"],
            type=ScopeType.FUNCTION,
            symbol_count=8,
            parent_path=[],
        ),
        ScopeExpectation(
            path=["exception_with_shadowing"],
            type=ScopeType.FUNCTION,
            symbol_count=5,
            parent_path=[],
        ),
        ScopeExpectation(
            path=["nested_exception_blocks"],
            type=ScopeType.FUNCTION,
            symbol_count=10,
            parent_path=[],
        ),
        ScopeExpectation(
            path=["exception_with_imports"],
            type=ScopeType.FUNCTION,
            symbol_count=15,
            parent_path=[],
        ),
        ScopeExpectation(
            path=["multiple_exception_types"],
            type=ScopeType.FUNCTION,
            symbol_count=13,
            parent_path=[],
        ),
        ScopeExpectation(
            path=["exception_in_comprehension"],
            type=ScopeType.FUNCTION,
            symbol_count=4,
            parent_path=[],
        ),
        ScopeExpectation(
            path=["exception_in_nested_function"],
            type=ScopeType.FUNCTION,
            symbol_count=5,
            parent_path=[],
        ),
        ScopeExpectation(
            path=["exception_in_nested_function", "inner_with_exception"],
            type=ScopeType.FUNCTION,
            symbol_count=7,
            parent_path=["exception_in_nested_function"],
        ),
        ScopeExpectation(
            path=["exception_with_walrus_operator"],
            type=ScopeType.FUNCTION,
            symbol_count=9,
            parent_path=[],
        ),
        ScopeExpectation(
            path=["compute_risky_value"],
            type=ScopeType.FUNCTION,
            symbol_count=0,
            parent_path=[],
        ),
        ScopeExpectation(
            path=["handle_error"],
            type=ScopeType.FUNCTION,
            symbol_count=1,
            parent_path=[],
        ),
        ScopeExpectation(
            path=["finalize_success"],
            type=ScopeType.FUNCTION,
            symbol_count=0,
            parent_path=[],
        ),
        ScopeExpectation(
            path=["cleanup_resources"],
            type=ScopeType.FUNCTION,
            symbol_count=0,
            parent_path=[],
        ),
    ]

    symbol_expectations = [
        SymbolExpectation("Any", [], "Any", "exceptions.py"),
        SymbolExpectation("basic_exception_handling", [], "basic_exception_handling", "exceptions.py"),
        SymbolExpectation("exception_with_shadowing", [], "exception_with_shadowing", "exceptions.py"),
        SymbolExpectation("nested_exception_blocks", [], "nested_exception_blocks", "exceptions.py"),
        SymbolExpectation("exception_with_imports", [], "exception_with_imports", "exceptions.py"),
        SymbolExpectation("multiple_exception_types", [], "multiple_exception_types", "exceptions.py"),
        SymbolExpectation("exception_in_comprehension", [], "exception_in_comprehension", "exceptions.py"),
        SymbolExpectation("exception_in_nested_function", [], "exception_in_nested_function", "exceptions.py"),
        SymbolExpectation("exception_with_walrus_operator", [], "exception_with_walrus_operator", "exceptions.py"),
        SymbolExpectation("compute_risky_value", [], "compute_risky_value", "exceptions.py"),
        SymbolExpectation("handle_error", [], "handle_error", "exceptions.py"),
        SymbolExpectation("finalize_success", [], "finalize_success", "exceptions.py"),
        SymbolExpectation("cleanup_resources", [], "cleanup_resources", "exceptions.py"),
        SymbolExpectation(
            "outer_variable",
            ["basic_exception_handling"],
            "basic_exception_handling.outer_variable",
            "exceptions.py",
        ),
        SymbolExpectation(
            "try_variable",
            ["basic_exception_handling"],
            "basic_exception_handling.try_variable",
            "exceptions.py",
        ),
        SymbolExpectation(
            "result",
            ["basic_exception_handling"],
            "basic_exception_handling.result",
            "exceptions.py",
        ),
        SymbolExpectation(
            "exception",
            ["basic_exception_handling"],
            "basic_exception_handling.exception",
            "exceptions.py",
        ),
        SymbolExpectation(
            "except_variable",
            ["basic_exception_handling"],
            "basic_exception_handling.except_variable",
            "exceptions.py",
        ),
        SymbolExpectation(
            "error_message",
            ["basic_exception_handling"],
            "basic_exception_handling.error_message",
            "exceptions.py",
        ),
        SymbolExpectation(
            "else_variable",
            ["basic_exception_handling"],
            "basic_exception_handling.else_variable",
            "exceptions.py",
        ),
        SymbolExpectation(
            "finally_variable",
            ["basic_exception_handling"],
            "basic_exception_handling.finally_variable",
            "exceptions.py",
        ),
        SymbolExpectation(
            "shadowed_name",
            ["exception_with_shadowing"],
            "exception_with_shadowing.shadowed_name",
            "exceptions.py",
        ),
        SymbolExpectation(
            "operation_result",
            ["exception_with_shadowing"],
            "exception_with_shadowing.operation_result",
            "exceptions.py",
        ),
        SymbolExpectation(
            "zero_div_exception",
            ["exception_with_shadowing"],
            "exception_with_shadowing.zero_div_exception",
            "exceptions.py",
        ),
        SymbolExpectation(
            "handler_variable",
            ["exception_with_shadowing"],
            "exception_with_shadowing.handler_variable",
            "exceptions.py",
        ),
        SymbolExpectation(
            "after_blocks",
            ["exception_with_shadowing"],
            "exception_with_shadowing.after_blocks",
            "exceptions.py",
        ),
        SymbolExpectation(
            "outer_scope",
            ["nested_exception_blocks"],
            "nested_exception_blocks.outer_scope",
            "exceptions.py",
        ),
        SymbolExpectation(
            "outer_try",
            ["nested_exception_blocks"],
            "nested_exception_blocks.outer_try",
            "exceptions.py",
        ),
        SymbolExpectation(
            "inner_try",
            ["nested_exception_blocks"],
            "nested_exception_blocks.inner_try",
            "exceptions.py",
        ),
        SymbolExpectation(
            "risky_operation",
            ["nested_exception_blocks"],
            "nested_exception_blocks.risky_operation",
            "exceptions.py",
        ),
        SymbolExpectation(
            "inner_exception",
            ["nested_exception_blocks"],
            "nested_exception_blocks.inner_exception",
            "exceptions.py",
        ),
        SymbolExpectation(
            "inner_except",
            ["nested_exception_blocks"],
            "nested_exception_blocks.inner_except",
            "exceptions.py",
        ),
        SymbolExpectation(
            "inner_finally",
            ["nested_exception_blocks"],
            "nested_exception_blocks.inner_finally",
            "exceptions.py",
        ),
        SymbolExpectation(
            "outer_exception",
            ["nested_exception_blocks"],
            "nested_exception_blocks.outer_exception",
            "exceptions.py",
        ),
        SymbolExpectation(
            "outer_except",
            ["nested_exception_blocks"],
            "nested_exception_blocks.outer_except",
            "exceptions.py",
        ),
        SymbolExpectation(
            "outer_finally",
            ["nested_exception_blocks"],
            "nested_exception_blocks.outer_finally",
            "exceptions.py",
        ),
        SymbolExpectation(
            "handling_variable",
            ["multiple_exception_types"],
            "multiple_exception_types.handling_variable",
            "exceptions.py",
        ),
        SymbolExpectation(
            "try_variable",
            ["multiple_exception_types"],
            "multiple_exception_types.try_variable",
            "exceptions.py",
        ),
        SymbolExpectation(
            "potentially_failing_operation",
            ["multiple_exception_types"],
            "multiple_exception_types.potentially_failing_operation",
            "exceptions.py",
        ),
        SymbolExpectation(
            "value_error",
            ["multiple_exception_types"],
            "multiple_exception_types.value_error",
            "exceptions.py",
        ),
        SymbolExpectation(
            "value_error_handler",
            ["multiple_exception_types"],
            "multiple_exception_types.value_error_handler",
            "exceptions.py",
        ),
        SymbolExpectation(
            "type_error",
            ["multiple_exception_types"],
            "multiple_exception_types.type_error",
            "exceptions.py",
        ),
        SymbolExpectation(
            "type_error_handler",
            ["multiple_exception_types"],
            "multiple_exception_types.type_error_handler",
            "exceptions.py",
        ),
        SymbolExpectation(
            "key_or_index_error",
            ["multiple_exception_types"],
            "multiple_exception_types.key_or_index_error",
            "exceptions.py",
        ),
        SymbolExpectation(
            "combined_handler",
            ["multiple_exception_types"],
            "multiple_exception_types.combined_handler",
            "exceptions.py",
        ),
        SymbolExpectation(
            "general_exception",
            ["multiple_exception_types"],
            "multiple_exception_types.general_exception",
            "exceptions.py",
        ),
        SymbolExpectation(
            "general_handler",
            ["multiple_exception_types"],
            "multiple_exception_types.general_handler",
            "exceptions.py",
        ),
        SymbolExpectation(
            "else_handler",
            ["multiple_exception_types"],
            "multiple_exception_types.else_handler",
            "exceptions.py",
        ),
        SymbolExpectation(
            "finally_handler",
            ["multiple_exception_types"],
            "multiple_exception_types.finally_handler",
            "exceptions.py",
        ),
        SymbolExpectation(
            "outer_value",
            ["exception_in_comprehension"],
            "exception_in_comprehension.outer_value",
            "exceptions.py",
        ),
        SymbolExpectation(
            "comprehension_with_exceptions",
            ["exception_in_comprehension"],
            "exception_in_comprehension.comprehension_with_exceptions",
            "exceptions.py",
        ),
        SymbolExpectation(
            "comprehension_exception",
            ["exception_in_comprehension"],
            "exception_in_comprehension.comprehension_exception",
            "exceptions.py",
        ),
        SymbolExpectation(
            "exception_in_comprehension_handler",
            ["exception_in_comprehension"],
            "exception_in_comprehension.exception_in_comprehension_handler",
            "exceptions.py",
        ),
        SymbolExpectation(
            "outer_exception_variable",
            ["exception_in_nested_function"],
            "exception_in_nested_function.outer_exception_variable",
            "exceptions.py",
        ),
        SymbolExpectation(
            "inner_with_exception",
            ["exception_in_nested_function"],
            "exception_in_nested_function.inner_with_exception",
            "exceptions.py",
        ),
        SymbolExpectation(
            "outer_try",
            ["exception_in_nested_function"],
            "exception_in_nested_function.outer_try",
            "exceptions.py",
        ),
        SymbolExpectation(
            "outer_exception",
            ["exception_in_nested_function"],
            "exception_in_nested_function.outer_exception",
            "exceptions.py",
        ),
        SymbolExpectation(
            "outer_except",
            ["exception_in_nested_function"],
            "exception_in_nested_function.outer_except",
            "exceptions.py",
        ),
        SymbolExpectation(
            "inner_variable",
            ["exception_in_nested_function", "inner_with_exception"],
            "exception_in_nested_function.inner_with_exception.inner_variable",
            "exceptions.py",
        ),
        SymbolExpectation(
            "inner_try",
            ["exception_in_nested_function", "inner_with_exception"],
            "exception_in_nested_function.inner_with_exception.inner_try",
            "exceptions.py",
        ),
        SymbolExpectation(
            "inner_operation",
            ["exception_in_nested_function", "inner_with_exception"],
            "exception_in_nested_function.inner_with_exception.inner_operation",
            "exceptions.py",
        ),
        SymbolExpectation(
            "inner_zero_error",
            ["exception_in_nested_function", "inner_with_exception"],
            "exception_in_nested_function.inner_with_exception.inner_zero_error",
            "exceptions.py",
        ),
        SymbolExpectation(
            "inner_except",
            ["exception_in_nested_function", "inner_with_exception"],
            "exception_in_nested_function.inner_with_exception.inner_except",
            "exceptions.py",
        ),
        SymbolExpectation(
            "access_outer",
            ["exception_in_nested_function", "inner_with_exception"],
            "exception_in_nested_function.inner_with_exception.access_outer",
            "exceptions.py",
        ),
        SymbolExpectation(
            "inner_finally",
            ["exception_in_nested_function", "inner_with_exception"],
            "exception_in_nested_function.inner_with_exception.inner_finally",
            "exceptions.py",
        ),
        SymbolExpectation(
            "exception",
            ["exception_with_walrus_operator"],
            "exception_with_walrus_operator.exception",
            "exceptions.py",
        ),
        SymbolExpectation(
            "try_walrus",
            ["exception_with_walrus_operator"],
            "exception_with_walrus_operator.try_walrus",
            "exceptions.py",
        ),
        SymbolExpectation(
            "try_result",
            ["exception_with_walrus_operator"],
            "exception_with_walrus_operator.try_result",
            "exceptions.py",
        ),
        SymbolExpectation(
            "except_walrus",
            ["exception_with_walrus_operator"],
            "exception_with_walrus_operator.except_walrus",
            "exceptions.py",
        ),
        SymbolExpectation(
            "except_result",
            ["exception_with_walrus_operator"],
            "exception_with_walrus_operator.except_result",
            "exceptions.py",
        ),
        SymbolExpectation(
            "else_walrus",
            ["exception_with_walrus_operator"],
            "exception_with_walrus_operator.else_walrus",
            "exceptions.py",
        ),
        SymbolExpectation(
            "else_result",
            ["exception_with_walrus_operator"],
            "exception_with_walrus_operator.else_result",
            "exceptions.py",
        ),
        SymbolExpectation(
            "finally_walrus",
            ["exception_with_walrus_operator"],
            "exception_with_walrus_operator.finally_walrus",
            "exceptions.py",
        ),
        SymbolExpectation(
            "finally_result",
            ["exception_with_walrus_operator"],
            "exception_with_walrus_operator.finally_result",
            "exceptions.py",
        ),
        SymbolExpectation(
            "error",
            ["handle_error"],
            "handle_error.error",
            "exceptions.py",
        ),
    ]

    @pytest.fixture
    def module_scope(self) -> ScopeNode[Any]:
        filepath = Path("tests/examples/scope/exceptions.py")
        return self.analyze_file(filepath)

    def test_complete_scope_and_symbol_analysis(self, module_scope: ScopeNode[Any]) -> None:
        self.validate_complete_analysis(module_scope, self.scope_expectations, self.symbol_expectations)
