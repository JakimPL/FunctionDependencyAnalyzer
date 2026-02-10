from pydepgraph.exceptions.base import PDGException


class PDGImportError(PDGException):
    """A general import error."""


class PDGImportResolutionError(PDGImportError):
    """Raised when an import cannot be resolved."""


class PDGModuleSpecError(PDGImportResolutionError):
    """Raised when there is an issue with a module spec during import resolution."""


class PDGPathResolutionError(PDGModuleSpecError):
    """Raised when a path cannot be resolved against any candidate base path or sys.path entry."""


class PDGEmptyOriginError(PDGModuleSpecError):
    """Raised when a module spec has an empty origin."""


class PDGFrozenOriginError(PDGModuleSpecError):
    """Raised when a module spec has a frozen origin."""


class PDGOriginFileNotFoundError(PDGModuleSpecError, FileNotFoundError):
    """Raised when a module spec has an origin path that does not exist."""


class PDGInvalidOriginTypeError(PDGModuleSpecError):
    """Raised when a module spec has an invalid origin type for its origin."""


class PDGMissingModuleSpecError(PDGModuleSpecError):
    """Raised when a module spec cannot be found for a given module name."""


class PDGSourceFileOutsideProjectError(PDGModuleSpecError):
    """Raised when the provided source file is outside the analyzed package/module."""


class PDGMissingModuleNameError(PDGImportError):
    """Raised when a module name is empty or cannot be determined."""


class PDGRelativeBasePathError(PDGImportError):
    """Raised when a relative path is provided as the base path."""
