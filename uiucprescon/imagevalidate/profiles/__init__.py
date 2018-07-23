import inspect

from .absProfile import AbsProfile
import importlib
import importlib.util
import pkgutil

__all__ = [
    "AbsProfile",
]

valid_profiles = []


def _load():
    """Dynamically load all the profiles with AbsProfile in into the
    profiles namespace"""

    def is_profile(i):
        if not inspect.isclass(i):
            return False
        if inspect.isabstract(i):
            return False
        return True

    for loader, module_name, is_pkgin in pkgutil.walk_packages(__path__):
        mod = importlib.import_module(f".{module_name}", __package__)
        for name, module_class in inspect.getmembers(mod, is_profile):
            if issubclass(module_class, AbsProfile):
                globals()[module_class.__name__] = module_class
                # __all__.append(module_class.__name__)
                valid_profiles.append(module_class.__name__)


_load()
__all__ += valid_profiles
