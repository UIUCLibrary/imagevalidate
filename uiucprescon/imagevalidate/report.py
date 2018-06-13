import typing


class Report:
    def __init__(self) -> None:
        self._properties: typing.Dict[str, str] = dict()

    @property
    def valid(self) -> bool:
        return True
