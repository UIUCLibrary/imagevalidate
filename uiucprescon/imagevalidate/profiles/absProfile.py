import abc
import collections
import typing

import py3exiv2bind
from typing import Dict, List, Optional, Set
from uiucprescon.imagevalidate import Report, IssueCategory, messages
from uiucprescon.imagevalidate.report import Result, ResultCategory


class AbsProfile(metaclass=abc.ABCMeta):
    """Base class for metadata validation.
    Implement the validate method when creating new profile"""

    expected_metadata_constants: Dict[str, str] = dict()
    expected_metadata_any_value: List[str] = list()
    expected_metadata_no_value: List[str] = list()
    ignored_metadata_fields: List[str] = list()
    valid_extensions: Set[str] = set()

    @staticmethod
    @abc.abstractmethod
    def profile_name() -> str:
        pass

    @abc.abstractmethod
    def validate(self, file: str) -> Report:
        """Validate a file

        Args:
            file: file path to the file to be validate

        Returns:
            Returns a report object
        """

    @classmethod
    def _get_metadata_static_values(cls, image: py3exiv2bind.Image) \
            -> Dict[str, Result]:

        data = dict()
        for key, value in cls.expected_metadata_constants.items():
            data[key] = Result(
                expected=value,
                actual=image.metadata.get(key)
            )
        return data

    @classmethod
    def _get_metadata_has_values(cls, image: py3exiv2bind.Image) -> \
            Dict[str, Result]:

        data = dict()
        for key in cls.expected_metadata_any_value:
            data[key] = Result(
                expected=ResultCategory.ANY,
                actual=image.metadata.get(key)
            )
        return data

    @classmethod
    def _get_metadata_ignored_values(cls, image) -> Dict[str, Result]:
        data = dict()
        for key in cls.ignored_metadata_fields:
            field = image.metadata.get(key)
            if field is None:
                continue
            if field.strip() == "":
                continue
            data[key] = Result(expected=ResultCategory.IGNORED, actual=field)
        return data

    @classmethod
    def _get_metadata_expected_no_value(cls, image) -> Dict[str, Result]:
        data = dict()
        for key in cls.expected_metadata_no_value:
            field = image.metadata.get(key)
            if field is None:
                continue
            if field.strip() == "":
                continue
            data[key] = Result(expected=ResultCategory.NONE, actual=field)

        return data

    @staticmethod
    def generate_error_msg(category: IssueCategory, field: str,
                           report_data: Result) -> str:

        message_types: Dict[IssueCategory, messages.AbsMessage] = {
            IssueCategory.INVALID_DATA: messages.InvalidData(),
            IssueCategory.EMPTY_DATA: messages.EmptyData(),
            IssueCategory.MISSING_FIELD: messages.MissingField(),
            IssueCategory.IGNORED_FIELD: messages.IgnoredField(),
            IssueCategory.EXPECTED_EMPTY_FIELD: messages.FieldExpectedEmpty(),
        }

        if category in message_types:

            message_generator = \
                messages.MessageGenerator(message_types[category])

            return message_generator.generate_message(field, report_data)

        return "Unknown error type {} with {}".format(category, field)

    @staticmethod
    def analyze_data_for_issues(result: Result) -> Optional[IssueCategory]:
        if result.expected is not ResultCategory.NONE \
                and result.actual is None:

            return IssueCategory.MISSING_FIELD

        if result.expected is ResultCategory.IGNORED \
                and result.actual is not ResultCategory.NONE:

            return IssueCategory.IGNORED_FIELD

        if result.expected is ResultCategory.NONE \
                and result.actual is not ResultCategory.NONE:

            return IssueCategory.EXPECTED_EMPTY_FIELD

        if result.actual == "":
            return IssueCategory.EMPTY_DATA

        if result.actual != result.expected and \
                result.expected is not ResultCategory.ANY:

            return IssueCategory.INVALID_DATA

        return None

    @classmethod
    def get_data_from_image(cls, filename: str) \
            -> Dict[str, Result]:
        image = py3exiv2bind.Image(filename)
        data: Dict[str, Result] = dict()
        data.update(cls._get_metadata_has_values(image))
        data.update(cls._get_metadata_expected_no_value(image))
        data.update(cls._get_metadata_ignored_values(image))
        data.update(cls._get_metadata_static_values(image))
        return data

    def analyze(self, report_data) -> typing.Dict[IssueCategory, list]:

        analysis: typing.Dict[IssueCategory, list] = \
            collections.defaultdict(list)

        for key, result in report_data.items():
            issue_category = self.analyze_data_for_issues(result)
            if issue_category:
                message = self.generate_error_msg(issue_category, key, result)
                analysis[issue_category].append(message)

        return analysis
