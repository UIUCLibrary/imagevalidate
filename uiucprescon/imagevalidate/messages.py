import abc

from uiucprescon.imagevalidate import report


class AbsMessage(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def generate_message(self, field: str, data: report.Result) -> str:
        pass


class InvalidData(AbsMessage):

    def generate_message(self, field: str, data: report.Result) -> str:
        return f'Invalid match for "{field}". ' \
               f'Expected: "{data.expected}". ' \
               f'Got: "{data.actual}".'


class EmptyData(AbsMessage):

    def generate_message(self, field: str, data: report.Result) -> str:
        return f'The "{field}" field exists but contains no data.'


class MissingField(AbsMessage):

    def generate_message(self, field: str, data: report.Result) -> str:
        return f'No metadata field for "{field}" found in file.'


class IgnoredField(AbsMessage):

    def generate_message(self, field: str, data: report.Result) -> str:
        return f"Note: {field} is expected to be absent; if it is present, " \
               f"the values will not be used."


class FieldExpectedEmpty(AbsMessage):

    def generate_message(self, field: str, data: report.Result) -> str:
        return f"Included invalid field {field}"


class MessageGenerator:

    def __init__(self, strategy: AbsMessage) -> None:
        self._strategy = strategy

    def generate_message(self, field: str, data: report.Result) -> str:
        return self._strategy.generate_message(field, data)
