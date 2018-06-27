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
        self._analysis_data: Dict[str, List[str]] = dict()

    @property
    def valid(self) -> bool:
        return len(self._analysis_data.items()) == 0

    def issues(self, issue_type=None) -> List[str]:
        if issue_type:
            return self._analysis_data.get(issue_type, list())
        else:
            issues = []
            for issue_group in self._analysis_data.values():
                issues += issue_group
            return issues

    def __str__(self) -> str:

        issue_str = "\n".join(self.issues())

        return "File: {}\n{}".format(self.filename, issue_str)

    def _add_issue(self, issue):
        self._issues.append(issue)