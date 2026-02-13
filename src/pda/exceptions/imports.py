from pda.exceptions.base import PDAException


class PDAImportPathError(PDAException):
    """A general import path error."""


class PDASourceFileOutsideProjectError(PDAImportPathError):
    """Raised when the provided source file is outside the analyzed package/module."""


class PDARelativeBasePathError(PDAImportPathError):
    """Raised when a relative path is provided as the base path."""


class PDAPathResolutionError(PDAImportPathError):
    """Raised when a path cannot be resolved against any candidate base path or sys.path entry."""
