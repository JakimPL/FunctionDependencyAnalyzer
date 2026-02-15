from enum import IntFlag, auto
from typing import List


class ImportScope(IntFlag):
    NONE = 0

    # Base branches
    IF = auto()  # also ELIF
    ELIF = auto()
    ELSE = auto()
    CASE = auto()
    DEFAULT = auto()
    TRY = auto()
    EXCEPT = auto()
    TRY_ELSE = auto()
    FINALLY = auto()

    # Loops, comprehensions and context managers
    LOOP = auto()  # for, while, comprehensions
    WITH = auto()

    # Definitions
    CLASS = auto()  # inside class def
    FUNCTION = auto()  # inside function def body
    DECORATOR = auto()

    # Special scopes
    TYPE_CHECKING = auto()  # `if TYPE_CHECKING` and variants
    MAIN = auto()  # `if __name__ == "__main__"`` and variants

    # Combinations
    IF_ELSE = IF | ELSE
    ERROR_HANDLING = TRY | EXCEPT | TRY_ELSE | FINALLY
    MATCH_CASE = CASE | DEFAULT
    BRANCH = IF_ELSE | MATCH_CASE | ERROR_HANDLING
    DEFINITION = CLASS | FUNCTION

    def validate(self) -> None:
        if self & ImportScope.TYPE_CHECKING and not self & ImportScope.IF_ELSE:
            raise ValueError("TYPE_CHECKING flag must be combined with IF or ELSE")

        if self & ImportScope.MAIN and not self & ImportScope.IF_ELSE:
            raise ValueError("MAIN flag must be combined with IF or ELSE")

        if self & ImportScope.DEFAULT and not self & ImportScope.CASE:
            raise ValueError("DEFAULT flag must be combined with CASE")

        if self & ImportScope.DECORATOR and not self & ImportScope.FUNCTION:
            raise ValueError("DECORATOR flag must be combined with FUNCTION")

    def __repr__(self) -> str:
        if self == ImportScope.NONE:
            return "NONE"

        composite_flags = {
            ImportScope.IF_ELSE,
            ImportScope.ERROR_HANDLING,
            ImportScope.MATCH_CASE,
            ImportScope.BRANCH,
            ImportScope.DEFINITION,
        }

        flags: List[str] = [
            name
            for flag in ImportScope
            if (self & flag)
            and flag != ImportScope.NONE
            and flag not in composite_flags
            and (name := flag.name) is not None
        ]

        return " | ".join(sorted(flags))
