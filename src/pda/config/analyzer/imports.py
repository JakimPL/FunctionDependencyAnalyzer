from typing import Optional

from pydantic import Field

from pda.config.base import BaseConfig
from pda.config.scan import ModuleScanConfig


class ModuleImportsAnalyzerConfig(BaseConfig):
    module_scan: ModuleScanConfig = Field(
        default=ModuleScanConfig(
            scan_stdlib=False,
            scan_external=False,
            scan_uninstalled=False,
            collect_metadata=False,
            hide_private=True,
        ),
        description="Configuration for scanning modules during import analysis.",
    )

    ignore_cycles: bool = Field(default=False, description="Ignore cycles in the dependency graph.")
    follow_conditional: bool = Field(default=True, description="Analyze if/try/except branches.")
    max_depth: Optional[int] = Field(
        default=None,
        description="Maximum depth for recursion. None means no limit.",
    )

    @property
    def scan_stdlib(self) -> bool:
        return self.module_scan.scan_stdlib

    @property
    def scan_external(self) -> bool:
        return self.module_scan.scan_external

    @property
    def scan_uninstalled(self) -> bool:
        return self.module_scan.scan_uninstalled

    @property
    def collect_metadata(self) -> bool:
        return self.module_scan.collect_metadata

    @property
    def hide_private(self) -> bool:
        return self.module_scan.hide_private
