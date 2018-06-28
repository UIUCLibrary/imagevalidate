import abc

import py3exiv2bind
from typing import Dict, List, Optional
from uiucprescon.imagevalidate import Report, IssueCategory
from uiucprescon.imagevalidate.report import Result


class AbsProfile(metaclass=abc.ABCMeta):
    expected_metadata_constants: Dict[str, str] = dict()
    expected_metadata_any_value: List[str] = list()

    @abc.abstractmethod
    def validate(self, file: str) -> Report:
        """ Validate a file

        Args:
            file: file path to the file to be validate

        Returns:
            Returns a report object
        """
        pass

    @classmethod
    def _get_metadata_static_values(cls, image: py3exiv2bind.Image):
        data = dict()
        for key, value in cls.expected_metadata_constants.items():
            data[key] = Result(
                expected=value,
                actual=image.metadata.get(key)
            )
        return data

    @classmethod
    def _get_metadata_has_values(cls, image):
        data = dict()
        for key in cls.expected_metadata_any_value:
            data[key] = Result(
                expected=None,
                actual=image.metadata.get(key)
            )
        return data

    @staticmethod
    def generate_msg(category: IssueCategory, field, report_data)->str:
        # TODO: refactor to a strategy pattern or a factory pattern

        if category == IssueCategory.INVALID_DATA:
            data_expected = report_data.expected
            data_got = report_data.actual
            report_string = \
                "Invalid match for \"{}\". " \
                "Expected: \"{}\". Got: \"{}\".".format(
                    field, data_expected, data_got)
            return report_string

        if category == IssueCategory.EMPTY:
            return "The \"{}\" field is empty.".format(field)

        if category == IssueCategory.MISSING:
            return "No metadata for \"{}\" found in file.".format(field)

        return "Unknown error with {}".format(field)

    @staticmethod
    def analyze_data_for_issues(result: Result) -> Optional[IssueCategory]:
        if result.actual is None:
            return IssueCategory.MISSING

        if result.actual is "":
            return IssueCategory.EMPTY

        if result.actual != result.expected and result.expected is not None:
            return IssueCategory.INVALID_DATA
        return None
