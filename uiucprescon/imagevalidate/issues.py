from enum import Enum


class IssueCategory(Enum):
    VALID = 0
    EMPTY_DATA = 1
    MISSING_FIELD = 2
    INVALID_DATA = 3
    IGNORED_FIELD = 4
    EXPECTED_EMPTY_FIELD = 5
