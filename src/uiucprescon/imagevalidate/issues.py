"""Module for defining issue categories related to image validation."""

from enum import Enum


class IssueCategory(Enum):
    """Enum class defining issue categories."""

    VALID = 0
    EMPTY_DATA = 1
    MISSING_FIELD = 2
    INVALID_DATA = 3
