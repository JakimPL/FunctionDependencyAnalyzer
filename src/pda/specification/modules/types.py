from typing import Dict, TypeAlias

from pda.specification.modules.module import Module
from pda.specification.modules.module.categorized import CategorizedModule
from pda.specification.modules.module.category import ModuleCategory

ModuleDict: TypeAlias = Dict[str, Module]
CategorizedModuleDict: TypeAlias = Dict[str, CategorizedModule]
ModuleCollectionDict: TypeAlias = Dict[ModuleCategory, CategorizedModuleDict]
