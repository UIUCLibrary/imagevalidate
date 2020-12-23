"""Report generated from validation."""

from typing import NamedTuple, Optional, Dict, List, Union
from enum import Enum
from uiucprescon import imagevalidate


class ResultCategory(Enum):
    ANY = 0
    NONE = 1


class Result(NamedTuple):
    expected: Union[str, ResultCategory]
    actual: Optional[str]


class Report:
    """Validation report."""

    def __init__(self) -> None:
        """Access the results."""
        self._properties: Dict[str, Result] = dict()
        self.filename: Optional[str] = None

        self._data: Dict[imagevalidate.IssueCategory, List[str]] = dict()

    @property
    def valid(self) -> bool:
        """Image validity.

        Returns:
            Returns true if valid, else returns false

        """
        return len(self._data.items()) == 0

    def issues(self,
               issue_type: Optional[imagevalidate.IssueCategory] = None) \
            -> List[str]:
        """Issues or problems discovered."""
        if issue_type is not None:
            return self._data.get(issue_type, list())

        # In issue category is selected, return all
        return [issue for issues in
                self._data.values() for issue in issues]

    def __str__(self) -> str:
        """Provide summary of the report."""
        if not self.valid:
            issue_str = "\n".join(self.issues())
        else:
            issue_str = "No issues discovered"

        return "File: {}\n{}".format(self.filename, issue_str)
