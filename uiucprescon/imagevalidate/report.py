from uiucprescon import imagevalidate
from typing import NamedTuple, Optional, Dict, List, Union
from enum import Enum


class ResultCategory(Enum):
    ANY = 0
    NONE = 1


class Result(NamedTuple):
    expected: Union[str, ResultCategory]
    actual: Optional[str]


class Report:
    def __init__(self) -> None:
        self._properties: Dict[str, Result] = dict()
        self.filename: Optional[str] = None

        self._data: Dict[imagevalidate.IssueCategory, List[str]] = dict()

    @property
    def valid(self) -> bool:
        return len(self._data.items()) == 0

    def issues(self,
               issue_type: Optional[imagevalidate.IssueCategory]=None) \
            -> List[str]:

        if issue_type is not None:
            return self._data.get(issue_type, list())
        else:
            # In issue category is selected, return all
            return [issue for issues in
                    self._data.values() for issue in issues]

    def __str__(self) -> str:
        if not self.valid:
            issue_str = "\n".join(self.issues())
        else:
            issue_str = "No issues discovered"

        return "File: {}\n{}".format(self.filename, issue_str)
