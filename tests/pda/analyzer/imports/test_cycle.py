from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import pytest

from pda.analyzer.imports.cycle import CycleDetector, NodeState
from pda.config import ModuleImportsAnalyzerConfig
from pda.exceptions.analyzer import PDADependencyCycleError


def make_path(name: str) -> Path:
    return Path(f"/test/{name}.py")


class TestCycleDetector:
    @dataclass
    class TestCase:
        __test__ = False

        label: str
        ignore_cycles: bool
        current_path: List[Path]
        next_origin: Optional[Path]
        expected_cycle: bool
        expected_cycle_path: List[Path]

    test_cases = [
        TestCase(
            label="no_cycle_new_node",
            ignore_cycles=True,
            current_path=[make_path("a"), make_path("b")],
            next_origin=make_path("c"),
            expected_cycle=False,
            expected_cycle_path=[],
        ),
        TestCase(
            label="simple_cycle",
            ignore_cycles=True,
            current_path=[make_path("a"), make_path("b")],
            next_origin=make_path("a"),
            expected_cycle=True,
            expected_cycle_path=[make_path("a"), make_path("b"), make_path("a")],
        ),
        TestCase(
            label="self_loop",
            ignore_cycles=True,
            current_path=[make_path("a")],
            next_origin=make_path("a"),
            expected_cycle=True,
            expected_cycle_path=[make_path("a"), make_path("a")],
        ),
        TestCase(
            label="deep_cycle",
            ignore_cycles=True,
            current_path=[make_path("a"), make_path("b"), make_path("c"), make_path("d")],
            next_origin=make_path("b"),
            expected_cycle=True,
            expected_cycle_path=[make_path("a"), make_path("b"), make_path("c"), make_path("d"), make_path("b")],
        ),
        TestCase(
            label="none_origin_no_cycle",
            ignore_cycles=True,
            current_path=[make_path("a")],
            next_origin=None,
            expected_cycle=False,
            expected_cycle_path=[],
        ),
        TestCase(
            label="empty_path_no_cycle",
            ignore_cycles=True,
            current_path=[],
            next_origin=make_path("a"),
            expected_cycle=False,
            expected_cycle_path=[],
        ),
    ]

    @pytest.mark.parametrize("test_case", test_cases, ids=lambda tc: tc.label)
    def test_check_cycle(self, test_case: TestCase) -> None:
        config = ModuleImportsAnalyzerConfig(ignore_cycles=test_case.ignore_cycles)
        detector = CycleDetector(config)

        has_cycle = detector.check_cycle(test_case.current_path, test_case.next_origin)

        assert has_cycle == test_case.expected_cycle
        assert detector.cycle_detected == test_case.expected_cycle
        assert detector.cycle_path == test_case.expected_cycle_path

    def test_check_cycle_raises_when_ignore_cycles_false(self) -> None:
        config = ModuleImportsAnalyzerConfig(ignore_cycles=False)
        detector = CycleDetector(config)
        path_a = make_path("a")
        path_b = make_path("b")

        with pytest.raises(PDADependencyCycleError, match="Dependency cycle detected"):
            detector.check_cycle([path_a, path_b], path_a)

    def test_check_cycle_logs_when_ignore_cycles_true(self, caplog: pytest.LogCaptureFixture) -> None:
        config = ModuleImportsAnalyzerConfig(ignore_cycles=True)
        detector = CycleDetector(config)
        path_a = make_path("a")
        path_b = make_path("b")

        detector.check_cycle([path_a, path_b], path_a)

        assert "Cycle detected" in caplog.text

    def test_mark_visiting(self) -> None:
        config = ModuleImportsAnalyzerConfig()
        detector = CycleDetector(config)
        path_a = make_path("a")

        detector.mark_visiting(path_a)

        assert detector.get_state(path_a) == NodeState.VISITING

    def test_mark_visited(self) -> None:
        config = ModuleImportsAnalyzerConfig()
        detector = CycleDetector(config)
        path_a = make_path("a")

        detector.mark_visiting(path_a)
        detector.mark_visited(path_a)

        assert detector.get_state(path_a) == NodeState.VISITED

    def test_unvisited_state_default(self) -> None:
        config = ModuleImportsAnalyzerConfig()
        detector = CycleDetector(config)
        path_a = make_path("a")

        assert detector.get_state(path_a) == NodeState.UNVISITED

    def test_reset_clears_state(self) -> None:
        config = ModuleImportsAnalyzerConfig(ignore_cycles=True)
        detector = CycleDetector(config)
        path_a = make_path("a")
        path_b = make_path("b")

        detector.mark_visiting(path_a)
        detector.mark_visited(path_b)
        detector.check_cycle([path_a], path_a)

        detector.reset()

        assert not detector.cycle_detected
        assert detector.cycle_path == []
        assert detector.get_state(path_a) == NodeState.UNVISITED
        assert detector.get_state(path_b) == NodeState.UNVISITED

    def test_report_cycles_warns_when_cycle_detected(self) -> None:
        config = ModuleImportsAnalyzerConfig(ignore_cycles=True)
        detector = CycleDetector(config)
        path_a = make_path("a")
        path_b = make_path("b")

        detector.check_cycle([path_a, path_b], path_a)

        with pytest.warns(match="Import cycle detected during analysis"):
            detector.report_cycles()

    def test_report_cycles_no_warning_when_no_cycle(self) -> None:
        import warnings as warnings_module

        config = ModuleImportsAnalyzerConfig()
        detector = CycleDetector(config)

        with warnings_module.catch_warnings(record=True) as warning_list:
            warnings_module.simplefilter("always")
            detector.report_cycles()

        assert len(warning_list) == 0

    def test_cycle_path_is_copy(self) -> None:
        config = ModuleImportsAnalyzerConfig(ignore_cycles=True)
        detector = CycleDetector(config)
        path_a = make_path("a")
        path_b = make_path("b")

        detector.check_cycle([path_a, path_b], path_a)
        cycle_path = detector.cycle_path
        cycle_path.append(make_path("c"))

        assert len(detector.cycle_path) == 3
        assert make_path("c") not in detector.cycle_path

    def test_multiple_cycle_checks_updates_cycle_path(self) -> None:
        config = ModuleImportsAnalyzerConfig(ignore_cycles=True)
        detector = CycleDetector(config)
        path_a = make_path("a")
        path_b = make_path("b")
        path_c = make_path("c")

        detector.check_cycle([path_a], path_a)
        assert len(detector.cycle_path) == 2

        detector.check_cycle([path_a, path_b, path_c], path_b)
        assert len(detector.cycle_path) == 4
        assert detector.cycle_path == [path_a, path_b, path_c, path_b]
