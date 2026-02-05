from __future__ import annotations

import ast
from enum import StrEnum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from fda.node import ASTNodeWrapper, NodeWrapperMap


class SymbolKind(StrEnum):
    FUNCTION = "function"
    CLASS = "class"
    VARIABLE = "variable"
    MODULE = "module"


class ModuleAvailability(StrEnum):
    INSTALLED = "installed"
    MISSING = "missing"
    CONDITIONAL = "conditional"


class ModuleSpec(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    fqn: str = Field(description="Fully Qualified Name: 'package.submodule'")
    origin: Optional[Path] = Field(default=None, description="Absolute file path (None if builtin/uninstalled)")
    is_package: bool = Field(default=False)
    submodule_search_locations: List[Path] = Field(default_factory=list)


class Symbol(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    fqn: str = Field(description="Fully qualified name: module.path.ClassName")
    kind: SymbolKind
    wrapper: Optional[ASTNodeWrapper[Any]] = Field(default=None, description="For internal symbols")
    module_fqn: str = Field(description="Module where it's defined")


class ImportItem(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    original_name: str = Field(description="Name in source module")
    local_name: str = Field(description="Name in current scope (handles 'as')")
    symbol: Optional[Symbol] = Field(default=None, description="Resolved symbol (if available)")


class ImportCondition(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    branch_type: str = Field(description="'try' or 'except' or 'else'")
    exception_types: List[str] = Field(default_factory=list)


class ImportStatement(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    target_module: str = Field(description="What we're importing from")
    items: List[ImportItem] = Field(description="What we import")
    is_wildcard: bool = Field(default=False)
    scope_id: Optional[str] = Field(default=None, description="Identifier for the scope where import happens")
    condition: Optional[ImportCondition] = Field(default=None, description="If in try/except")
    lineno: int = Field(description="Line number in source file")


class Module(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    spec: ModuleSpec
    ast_tree: Optional[ast.AST] = Field(default=None, description="None if external/uninstalled")
    exports: Dict[str, Symbol] = Field(default_factory=dict, description="What this module exposes")
    imports: List[ImportStatement] = Field(default_factory=list)
    wrappers: NodeWrapperMap = Field(default_factory=dict, description="From NameResolver")
    availability: ModuleAvailability = Field(default=ModuleAvailability.INSTALLED)
    import_chain: List[str] = Field(default_factory=list, description="Chain of modules that led to this import")
