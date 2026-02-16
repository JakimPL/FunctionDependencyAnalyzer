from pda.constants import DELIMITER
from pda.specification import CategorizedModule
from pda.structures.node.base import Node


class ModuleNode(Node[CategorizedModule]):
    def __init__(self, module: CategorizedModule, *, ordinal: int = 0, level: int = 0) -> None:
        label = module.name.split(DELIMITER)[-1]
        details = module.name
        group = module.category.value
        super().__init__(
            item=module,
            ordinal=ordinal,
            label=label,
            details=details,
            level=level,
            group=group,
        )

    @property
    def module(self) -> CategorizedModule:
        return self.item
