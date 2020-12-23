"""Profiles for testing images against."""

import inspect
import abc

import importlib
import importlib.util
import pkgutil
from .absProfile import AbsProfile

__all__ = [
    "AbsProfile",
]

valid_profiles = []


def _load() -> None:
    """Dynamically load profiles with AbsProfile in the profiles namespace."""

    def is_profile(i: abc.ABCMeta) -> bool:
        if not inspect.isclass(i):
            return False
        if inspect.isabstract(i):
            return False
        return True

    module_path = __path__  # type: ignore

    for _, module_name, _ in \
            pkgutil.walk_packages(module_path):

        mod = importlib.import_module(f".{module_name}", __package__)
        for _, module_class in inspect.getmembers(mod, is_profile):
            if issubclass(module_class, AbsProfile):
                globals()[module_class.__name__] = module_class
                # __all__.append(module_class.__name__)
                valid_profiles.append(module_class.__name__)


_load()
__all__ += valid_profiles
