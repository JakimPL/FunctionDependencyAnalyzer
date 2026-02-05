from __future__ import annotations

from collections import deque
from typing import Deque, Dict, List, Optional, Set, Tuple

from fda.importer.config import ImportConfig
from fda.importer.graph import ModuleDependencyGraph
from fda.importer.spec import Module


class ModuleRegistry:
    def __init__(self, config: ImportConfig) -> None:
        self.config = config
        self.modules: Dict[str, Module] = {}
        self.pending: Set[str] = set()
        self.graph = ModuleDependencyGraph()

    def __call__(self, start_module: str) -> Set[str]:
        return self.traverse_dependencies(start_module)

    def __getitem__(self, fqn: str) -> Module:
        return self.modules[fqn]

    def register_module(self, module: Module) -> None:
        fqn = module.spec.fqn
        self.modules[fqn] = module
        self.graph.add_node(module)

        for import_stmt in module.imports:
            self.graph.add_dependency(fqn, import_stmt.target_module)

    def get(self, fqn: str) -> Optional[Module]:
        return self.modules.get(fqn)

    def has(self, fqn: str) -> bool:
        return fqn in self.modules

    def mark_pending(self, fqn: str) -> None:
        self.pending.add(fqn)

    def unmark_pending(self, fqn: str) -> None:
        self.pending.discard(fqn)

    def is_pending(self, fqn: str) -> bool:
        return fqn in self.pending

    def detect_cycles(self) -> List[List[str]]:
        return self.graph.find_cycles()

    def traverse_dependencies(
        self,
        start_module: str,
        visited: Optional[Set[str]] = None,
        depth: int = 0,
    ) -> Set[str]:
        if visited is None:
            visited = set()

        if start_module in visited:
            return visited

        if self.config.max_depth is not None and depth >= self.config.max_depth:
            return visited

        visited.add(start_module)

        module = self.get(start_module)
        if not module:
            return visited

        if not self.config.scan_external and module.spec.origin:
            if not self.config.is_internal_module(module.spec.origin):
                return visited

        for dependency in self.graph.get_dependencies(start_module):
            self.traverse_dependencies(dependency, visited, depth + 1)

        return visited

    def get_all_internal_modules(self) -> List[Module]:
        return [
            module
            for module in self.modules.values()
            if module.spec.origin and self.config.is_internal_module(module.spec.origin)
        ]

    def get_import_chain_to(self, target: str, start: Optional[str] = None) -> Optional[List[str]]:
        if start is None:
            internal = self.get_all_internal_modules()
            if not internal:
                return None
            start = internal[0].spec.fqn

        visited: Set[str] = set()
        queue: Deque[Tuple[str, List[str]]] = deque([(start, [start])])

        while queue:
            current, path = queue.popleft()

            if current == target:
                return path

            if current in visited:
                continue

            visited.add(current)

            for neighbor in self.graph.get_dependencies(current):
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))

        return None
