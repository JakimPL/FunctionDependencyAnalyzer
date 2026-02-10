from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, Type, TypeVar

import networkx as nx

from pydepgraph.config.graph import GraphOptions

T = TypeVar("T")


class BaseGraph(Generic[T], ABC):
    """
    Base graph class for Python Dependency Analyzer.
    """

    graph_type: Type[nx.Graph[T]]

    def __init_subclass__(cls, graph_type: Type[nx.Graph[T]] = nx.DiGraph) -> None:
        super().__init_subclass__()
        cls.graph_type = graph_type

    def __init__(self, options: Optional[GraphOptions] = None) -> None:
        self.config = options or GraphOptions()
        self._graph = self.__class__.graph_type()

    @abstractmethod
    def __call__(self, *args: Any, **kwargs: Any) -> nx.DiGraph:
        """
        Create the output graph based on the provided options.
        """

    def add_node(self, module: T) -> None:
        if not self._graph.has_node(module):
            self._graph.add_node(module)

    def add_edge(self, from_module: T, to_module: T) -> None:
        if from_module != to_module and not self._graph.has_edge(from_module, to_module):
            self.add_node(from_module)
            self.add_node(to_module)
            self._graph.add_edge(from_module, to_module)

    @property
    def has_cycles(self) -> bool:
        return not nx.is_directed_acyclic_graph(self._graph)

    def find_cycles(self) -> List[List[T]]:
        if self.has_cycles:
            return [list(cycle) for cycle in nx.simple_cycles(self._graph)]

        return []
