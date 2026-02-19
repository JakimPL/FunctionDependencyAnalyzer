from enum import StrEnum


class ModuleType(StrEnum):
    UNKNOWN = "unknown"
    MODULE = "module"
    PACKAGE = "package"
    NAMESPACE_PACKAGE = "namespace_package"
