import os
from uiucprescon import imagevalidate
from .profiles import AbsProfile


class Profile:

    def __init__(self, profile: AbsProfile) -> None:
        self._profile = profile

    def validate(self, file: str) -> imagevalidate.Report:
        if not os.path.exists(file):
            raise FileNotFoundError("Unable to locate {}".format(file))
        return self._profile.validate(file)
