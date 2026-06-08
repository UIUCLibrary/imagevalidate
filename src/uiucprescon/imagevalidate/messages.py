"""Creating messages."""

import abc

from uiucprescon.imagevalidate import report


class AbsMessage(metaclass=abc.ABCMeta):
    # pylint: disable=too-few-public-methods
    """Base class for messages."""

    @abc.abstractmethod
    def generate_message(self, field: str, data: report.Result) -> str:
        """Generate message as a string."""


class InvalidData(AbsMessage):
    # pylint: disable=too-few-public-methods
    """Invalid data."""

    def generate_message(self, field: str, data: report.Result) -> str:
        """Generate message as text."""
        return f'Invalid match for "{field}". ' \
               f'Expected: "{data.expected}". ' \
               f'Got: "{data.actual}".'


class EmptyData(AbsMessage):
    # pylint: disable=too-few-public-methods
    """Empty data."""

    def generate_message(self, field: str, data: report.Result) -> str:
        """Generate message as text."""
        return f'The "{field}" field exists but contains no data.'


class MissingField(AbsMessage):
    # pylint: disable=too-few-public-methods
    """Missing fields."""

    def generate_message(self, field: str, data: report.Result) -> str:
        """Generate message as text."""
        return f'No metadata field for "{field}" found in file.'


class MessageGenerator:
    # pylint: disable=too-few-public-methods
    """Message Generator."""

    def __init__(self, strategy: AbsMessage) -> None:
        """Set the strategy of used to generate a message.

        Args:
            strategy:
                Message strategy
        """
        self._strategy = strategy

    def generate_message(self, field: str, data: report.Result) -> str:
        """Generate a message string from the result."""
        return self._strategy.generate_message(field, data)
