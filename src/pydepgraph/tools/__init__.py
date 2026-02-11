from pydepgraph.tools.logger import setup_logger
from pydepgraph.tools.ordered_set import OrderedSet
from pydepgraph.tools.singleton import Singleton

logger = setup_logger()

__all__ = [
    "logger",
    "OrderedSet",
    "Singleton",
]
