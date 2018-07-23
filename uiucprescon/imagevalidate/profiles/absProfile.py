import abc

import py3exiv2bind
from typing import Dict, List, Optional, Set
from uiucprescon.imagevalidate import Report, IssueCategory, messages
from uiucprescon.imagevalidate.report import Result, ResultCategory


class AbsProfile(metaclass=abc.ABCMeta):
    """Base class for metadata validation.
    Implement the validate method when creating new profile"""

    expected_metadata_constants: Dict[str, str] = dict()
    expected_metadata_any_value: List[str] = list()
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
        pass
    # @abc.abstractmethod
    # def valid_extensions(cls)-> Iterable:
    #     return list()

    @classmethod
    def _get_metadata_static_values(cls, image: py3exiv2bind.Image)\
            ->Dict[str, Result]:

        data = dict()
        for key, value in cls.expected_metadata_constants.items():
            data[key] = Result(
                expected=value,
                actual=image.metadata.get(key)
            )
        return data

    @classmethod
    def _get_metadata_has_values(cls, image: py3exiv2bind.Image)->\
            Dict[str, Result]:

        data = dict()
        for key in cls.expected_metadata_any_value:
            data[key] = Result(
                expected=ResultCategory.ANY,
                actual=image.metadata.get(key)
            )
        return data

    @staticmethod
    def generate_error_msg(category: IssueCategory, field: str,
                           report_data: Result)->str:

        message_types: Dict[IssueCategory, messages.AbsMessage] = {
            IssueCategory.INVALID_DATA: messages.InvalidData(),
            IssueCategory.EMPTY_DATA: messages.EmptyData(),
            IssueCategory.MISSING_FIELD: messages.MissingField()
        }

        if category in message_types:

            message_generator = \
                messages.MessageGenerator(message_types[category])

            return message_generator.generate_message(field, report_data)

        return "Unknown error with {}".format(field)

    @staticmethod
    def analyze_data_for_issues(result: Result) -> Optional[IssueCategory]:
        if result.actual is None:
            return IssueCategory.MISSING_FIELD

        if result.actual is "":
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
        data.update(cls._get_metadata_static_values(image))
        return data
