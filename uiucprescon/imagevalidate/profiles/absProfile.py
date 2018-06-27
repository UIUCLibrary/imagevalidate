import abc

import py3exiv2bind
from typing import Dict, List
from uiucprescon.imagevalidate import Report
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

    @classmethod
    def parse_issues(cls, analysis, report_data):

        for field in analysis.get("missing", list()):
            yield "No metadata for \"{}\" found in file.".format(field)

        for field in analysis.get("empty", list()):
            yield "The \"{}\" field is empty.".format(field)

        for field in analysis.get("mismatch", list()):
            data_expected = report_data[field].expected
            data_got = report_data[field].actual
            report_string = \
                "Invalid match for \"{}\". " \
                "Expected: \"{}\". Got: \"{}\".".format(
                    field, data_expected, data_got)

            yield report_string
