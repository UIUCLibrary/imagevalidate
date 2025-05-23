"""Profile for validating images."""

import os
import inspect
from typing import Type, Set, Dict
from uiucprescon import imagevalidate
from . import profiles as profile_pkg

known_profiles: Dict[str, Type[profile_pkg.AbsProfile]] = {}


class Profile:
    """Profile loader for validating embedded metadata in image files."""

    def __init__(self, validation_profile: profile_pkg.AbsProfile) -> None:
        """Set the profile to validate against.

        Args:
            validation_profile:
        """
        self._profile = validation_profile

    def validate(self, file: str) -> imagevalidate.Report:
        """Validate the image file.

        Args:
            file:
                Path to image file to validate
        Returns:
            Report on validity of the file

        """
        if not os.path.exists(file):
            raise FileNotFoundError(f"Unable to locate {file}")
        return self._profile.validate(file)


def available_profiles() -> Set[str]:
    """Get the names of all available profiles.

    Returns:
        List of available profiles accessible in this version

    """
    known_package_profiles: Dict[str, Type[profile_pkg.AbsProfile]] = \
        get_profile_classes()

    return set(known_package_profiles.keys())


def get_profile(name: str) -> profile_pkg.AbsProfile:
    """Locate a profile based on the name of the class."""
    profiles = get_profile_classes()
    return profiles[name]()


def get_profile_classes():
    known_package_profiles: Dict[str, Type[profile_pkg.AbsProfile]] = {}
    profiles = \
        inspect.getmembers(
            profile_pkg,
            lambda m: inspect.isclass(m) and not inspect.isabstract(m)
        )

    for profile in profiles:
        known_package_profiles[profile[1].profile_name()] = profile[1]
    return known_package_profiles

known_profiles = get_profile_classes()
