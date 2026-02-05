from __future__ import annotations

from collections import defaultdict, deque
from typing import DefaultDict, Deque, Dict, List, Set

from fda.importer.spec import Module


class ModuleDependencyGraph:
    def __init__(self) -> None:
        self.nodes: Dict[str, Module] = {}
        self.edges: DefaultDict[str, Set[str]] = defaultdict(set)
        self.reverse_edges: DefaultDict[str, Set[str]] = defaultdict(set)

    def add_node(self, module: Module) -> None:
        self.nodes[module.spec.fqn] = module

    def add_dependency(self, from_module: str, to_module: str) -> None:
        self.edges[from_module].add(to_module)
        self.reverse_edges[to_module].add(from_module)

    def get_dependencies(self, module_fqn: str) -> Set[str]:
        return self.edges.get(module_fqn, set())

    def get_dependents(self, module_fqn: str) -> Set[str]:
        return self.reverse_edges.get(module_fqn, set())

    def find_cycles(self) -> List[List[str]]:
        cycles = []
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        path: List[str] = []

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.edges.get(node, set()):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])
                    return True

            path.pop()
            rec_stack.remove(node)
            return False

        for node in self.nodes:
            if node not in visited:
                dfs(node)

        return cycles

    def topological_sort(self) -> List[str]:
        in_degree = {node: 0 for node in self.nodes}
        for node in self.nodes:
            for neighbor in self.edges.get(node, set()):
                if neighbor in in_degree:
                    in_degree[neighbor] += 1

        queue: Deque[str] = deque([node for node, degree in in_degree.items() if degree == 0])
        sorted_nodes = []

        while queue:
            node = queue.popleft()
            sorted_nodes.append(node)

            for neighbor in self.edges.get(node, set()):
                if neighbor in in_degree:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)

        return sorted_nodes
