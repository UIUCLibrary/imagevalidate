import os


class Profile:

    def __init__(self, profile) -> None:
        self._profile = profile

    def validate(self, file):
        if not os.path.exists(file):
            raise FileNotFoundError("Unable to locate {}".format(file))
        return self._profile.validate(file)
