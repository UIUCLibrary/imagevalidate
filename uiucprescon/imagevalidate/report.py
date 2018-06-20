# import typing
from typing import NamedTuple, Optional, Dict, List, Union


class Result(NamedTuple):
    expected: Union[str, None]
    actual: str


class Report:
    def __init__(self) -> None:
        self._properties: Dict[str, Result] = dict()
        self.filename: Optional[str] = None
        self._issues: List[str] = list()

    @property
    def valid(self) -> bool:
        return len(self._issues) == 0

    @property
    def issues(self) -> List[str]:
        return self._issues

    def __str__(self) -> str:

        issue_str = "\n".join(self._issues)

        return "File: {}\n{}".format(self.filename, issue_str)
