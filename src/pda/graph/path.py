from pathlib import Path
from typing import override

from pda.graph.base import Graph
from pda.tools.paths import is_dir


class PathGraph(Graph[Path]):
    @override
    def label(self, node: Path) -> str:
        return node.name

    @override
    def group(self, node: Path) -> str:
        if is_dir(node):
            return "."

        return node.suffix
