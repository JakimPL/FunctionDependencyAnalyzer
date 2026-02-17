from pathlib import Path
from typing import List

from pydantic import Field

from pda.specification.base import Specification
from pda.specification.imports.path import ImportPath
from pda.specification.imports.scope import ImportScope
from pda.specification.source.span import SourceSpan


class ImportStatement(Specification):
    origin: Path = Field(..., description="The file from which this import statement was extracted")
    span: SourceSpan = Field(..., description="Source code span of the import statement")
    path: ImportPath = Field(
        ...,
        description="The import path, e.g. 'package.module' or 'package.module:ClassName'",
    )
    scopes: List[ImportScope] = Field(
        default_factory=list,
        description="Scope in which this import is executed, from innermost to outermost",
    )
