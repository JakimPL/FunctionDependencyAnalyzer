from pda.exceptions.base import PDAWarning


class PDAOptionsWarning(PDAWarning):
    """Warning related to PDA options."""


class PDAValidationOptionsWarning(PDAOptionsWarning):
    """Warning related to validation options."""


class PDACategoryDisabledWarning(PDAOptionsWarning):
    """Warning raised when a disabled category is tried to be accessed."""
