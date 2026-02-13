from typing import Optional

from pydantic import Field

from pda.config.base import BaseConfig
from pda.config.imports.output import ImportGraphNodeFormatEnum


class ModulesCollectorConfig(BaseConfig):
    scan_stdlib: bool = Field(default=False, description="Include standard library modules")
    scan_external: bool = Field(default=False, description="Include stdlib/site-packages")
    max_level: Optional[int] = Field(
        default=None,
        description="Maximum depth for collecting imports. None means no limit.",
    )
    node_format: ImportGraphNodeFormatEnum = Field(
        default=ImportGraphNodeFormatEnum.FULL,
        description="Output format for the import graph",
    )
