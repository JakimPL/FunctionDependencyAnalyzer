from typing import Dict, TypeAlias

from pda.specification.modules.categorized import CategorizedModule
from pda.specification.modules.category import ModuleCategory
from pda.specification.modules.module import Module

ModuleDict: TypeAlias = Dict[str, Module]
CategorizedModuleDict: TypeAlias = Dict[str, CategorizedModule]
ModuleCollectionDict: TypeAlias = Dict[ModuleCategory, CategorizedModuleDict]
