import os
import inspect
from typing import Type, Set, Dict
from uiucprescon import imagevalidate
from . import profiles as profile_pkg

known_profiles: Dict[str, Type[profile_pkg.AbsProfile]] = {}


class Profile:

    def __init__(self, profile: profile_pkg.AbsProfile) -> None:
        self._profile = profile

    def validate(self, file: str) -> imagevalidate.Report:
        if not os.path.exists(file):
            raise FileNotFoundError("Unable to locate {}".format(file))
        return self._profile.validate(file)


def available_profiles()-> Set[str]:
    """
    Get the names of all available profiles

    Returns: List of available profiles accessible in this version

    """
    return set(known_profiles.keys())


def get_profile(name: str):
    return known_profiles[name]()


profiles = inspect.getmembers(
    profile_pkg, lambda m: inspect.isclass(m) and not inspect.isabstract(m))

for profile in profiles:
    known_profiles[profile[0]] = profile[1]
