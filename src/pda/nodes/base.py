from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from typing import Dict, Generic, List, Optional, Set, Union

from anytree import LevelOrderIter

from pda.nodes.types import AnyNodeT
from pda.tools.ordered_set import OrderedSet
from pda.types import AnyT, HashableT


class BaseForest(ABC, Generic[HashableT, AnyT, AnyNodeT]):
    def __init__(self, items: Union[HashableT, Iterable[HashableT]]) -> None:
        self._mapping: Dict[AnyT, AnyNodeT] = {}
        self._items: List[AnyT] = self._prepare_inputs(items)
        self._roots: Set[AnyNodeT] = set()
        self()

    def __bool__(self) -> bool:
        return bool(self._mapping)

    def __call__(self) -> Set[AnyNodeT]:
        for item in self._items:
            self._build_tree(item)

        return self._roots

    def __iter__(self) -> Iterator[AnyNodeT]:
        for root in self._roots:
            yield from LevelOrderIter(root)

    def __getitem__(self, item: AnyT) -> AnyNodeT:
        item = self._prepare_item(item)
        return self._mapping[item]

    def _prepare_inputs(self, inputs: Union[HashableT, Iterable[HashableT]]) -> List[AnyT]:
        if isinstance(inputs, Iterable):
            items: OrderedSet[HashableT] = OrderedSet[HashableT](inputs)
            return list(map(self._prepare_input, items))

        return [self._prepare_input(inputs)]

    @property
    def roots(self) -> Set[AnyNodeT]:
        return self._roots.copy()

    @property
    def mapping(self) -> Dict[AnyT, AnyNodeT]:
        return self._mapping.copy()

    @abstractmethod
    def _input_to_item(self, inp: HashableT) -> AnyT: ...

    def _prepare_input(self, inp: HashableT) -> AnyT:
        item = self._input_to_item(inp)
        return self._prepare_item(item)

    def _prepare_item(self, item: AnyT) -> AnyT:
        return item

    @abstractmethod
    def _build_tree(
        self,
        item: AnyT,
        parent: Optional[AnyNodeT] = None,
    ) -> None: ...

    def _add_node(
        self,
        item: AnyT,
        parent: Optional[AnyNodeT] = None,
    ) -> Optional[AnyNodeT]:
        if item in self._mapping:
            return self[item]

        node = self._create_node(item, parent=parent)
        self._mapping[item] = node
        return node

    @abstractmethod
    def _create_node(
        self,
        item: AnyT,
        parent: Optional[AnyNodeT] = None,
    ) -> AnyNodeT: ...

    def get(self, item: AnyT) -> Optional[AnyNodeT]:
        item = self._prepare_item(item)
        return self._mapping.get(item)
