import abc
from uiucprescon.imagevalidate import Report


class AbsProfile(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def validate(self, file: str) -> Report:
        """ Validate a file

        Args:
            file: file path to the file to be validate

        Returns:
            Returns a report object
        """
        pass
