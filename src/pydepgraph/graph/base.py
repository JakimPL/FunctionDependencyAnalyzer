from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, Tuple, Type, TypeAlias, TypeVar

import networkx as nx

from pydepgraph.config.graph import GraphOptions

NodeT = TypeVar("NodeT")
Edge: TypeAlias = Tuple[NodeT, NodeT]


class BaseGraph(Generic[NodeT], ABC):
    """
    Base graph class for Python Dependency Analyzer.
    """

    graph_type: Type[nx.Graph]

    def __init_subclass__(cls, graph_type: Type[nx.Graph] = nx.DiGraph) -> None:
        super().__init_subclass__()
        cls.graph_type = graph_type

    def __init__(self, options: Optional[GraphOptions] = None) -> None:
        self.config = options or GraphOptions()
        self._graph = self.__class__.graph_type()

    def __len__(self) -> int:
        return int(self._graph.number_of_nodes())

    @abstractmethod
    def __call__(self, *args: Any, **kwargs: Any) -> nx.DiGraph:
        """
        Create the output graph based on the provided options.
        """

    def has_node(self, module: NodeT) -> bool:
        return bool(self._graph.has_node(module))

    def has_edge(self, from_module: NodeT, to_module: NodeT) -> bool:
        return bool(self._graph.has_edge(from_module, to_module))

    def add_node(self, module: NodeT) -> None:
        if not self.has_node(module):
            self._graph.add_node(module)

    def add_edge(self, from_module: NodeT, to_module: NodeT) -> None:
        if from_module != to_module and not self.has_edge(from_module, to_module):
            self.add_node(from_module)
            self.add_node(to_module)
            self._graph.add_edge(from_module, to_module)

    @property
    def empty(self) -> bool:
        return len(self) == 0

    @property
    def has_cycles(self) -> bool:
        return not nx.is_directed_acyclic_graph(self._graph)

    def find_cycle(self) -> Optional[List[NodeT]]:
        try:
            cycle: List[Edge[NodeT]] = nx.find_cycle(self._graph)
            return [cycle[0][0]] + [edge[1] for edge in cycle]
        except nx.NetworkXNoCycle:
            return None

    def find_cycles(self) -> List[List[NodeT]]:
        if self.has_cycles:
            return [list(cycle) for cycle in nx.simple_cycles(self._graph)]

        return []
