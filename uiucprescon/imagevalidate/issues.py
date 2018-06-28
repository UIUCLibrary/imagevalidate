from enum import Enum


class IssueCategory(Enum):
    VALID = 0
    EMPTY = 1
    MISSING = 2
    INVALID_DATA = 3
