import os
import inspect
from typing import Type, Set, Dict
from uiucprescon import imagevalidate
from . import profiles as profile_pkg

known_profiles: Dict[str, Type[profile_pkg.AbsProfile]] = {}


class Profile:
    """Profile loader for validating embedded metadata in image files"""

    def __init__(self, validation_profile: profile_pkg.AbsProfile) -> None:
        self._profile = validation_profile

    def validate(self, file: str) -> imagevalidate.Report:
        if not os.path.exists(file):
            raise FileNotFoundError("Unable to locate {}".format(file))
        return self._profile.validate(file)


def available_profiles()-> Set[str]:
    """Get the names of all available profiles

    Returns: List of available profiles accessible in this version

    """
    return set(known_profiles.keys())


def get_profile(name: str) -> profile_pkg.AbsProfile:
    """Locate a profile based on the name of the class"""
    return known_profiles[name]()


profiles = inspect.getmembers(
    profile_pkg, lambda m: inspect.isclass(m) and not inspect.isabstract(m))

for profile in profiles:
    known_profiles[profile[1].profile_name()] = profile[1]
