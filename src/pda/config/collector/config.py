from typing import Optional

from pydantic import Field

from pda.config.base import BaseConfig


class ModulesCollectorConfig(BaseConfig):
    scan_stdlib: bool = Field(default=False, description="Include standard library modules")
    scan_external: bool = Field(default=False, description="Include stdlib/site-packages")
    collect_metadata: bool = Field(default=False, description="Collect module metadata")
    max_level: Optional[int] = Field(
        default=None,
        description="Maximum depth for collecting imports. None means no limit.",
    )
