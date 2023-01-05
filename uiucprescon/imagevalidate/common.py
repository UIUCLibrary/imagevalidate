"""Common helper functions."""

import abc

import py3exiv2bind
import py3exiv2bind.core
from uiucprescon.imagevalidate import openjp2wrap  # type: ignore


class InvalidStrategy(Exception):
    """Invalid strategy is used."""


class AbsColorSpaceExtractor(metaclass=abc.ABCMeta):
    """Base class for extracting the color space from an image file."""

    @abc.abstractmethod
    def check(self, image: str) -> str:
        """Check the color space of a given file.

        Args:
            image:
                path to an image file

        Returns:
            color space name

        """


class ExtractColorSpace:
    """Strategy context for extract color space from a file."""

    def __init__(self, strategy: AbsColorSpaceExtractor) -> None:
        """Set the Strategy used for extracting the color space information.

        Args:
            strategy:
                Strategy to use
        """
        self.strategy = strategy

    def check(self, image: str) -> str:
        """Check the color space of a given file.

        Args:
            image:
                path to an image file

        Returns:
            color space name

        """
        return self.strategy.check(image)


class ColorSpaceIccDeviceModelCheck(AbsColorSpaceExtractor):
    """Extract color space by reading the device_model tag in the ICC profile.

    Useful for identifying sRGB.
    """

    def check(self, image: str) -> str:
        """Check the color space of a given file.

        Args:
            image:
                path to an image file

        Returns:
            color space name

        """
        exiv_image = py3exiv2bind.Image(image)
        try:
            icc = exiv_image.icc()
        except py3exiv2bind.core.NoICCError:
            raise InvalidStrategy("Unable to get ICC profile.")

        device_model = icc.get('device_model')
        if not device_model or \
                device_model.value.decode("ascii").rstrip(' \0') == '':
            raise InvalidStrategy("No device_model key found in icc profile")
        return str(device_model.value.decode("ascii").rstrip(' \0'))


class ColorSpaceIccPrefCcmCheck(AbsColorSpaceExtractor):
    """Extract color space from reading pref_ccm in the ICC profile header."""

    def check(self, image: str) -> str:
        """Check the color space of a given file.

        Args:
            image:
                path to an image file

        Returns:
            color space name

        """
        exiv2_image = py3exiv2bind.Image(image)
        try:
            icc = exiv2_image.icc()
        except py3exiv2bind.core.NoICCError as error:
            raise InvalidStrategy("Unable to get ICC profile."
                                  "Reason: {}".format(error))

        pref_ccm = icc.get("pref_ccm")
        if not pref_ccm or pref_ccm.value.decode("ascii").rstrip(' \0') == '':
            raise InvalidStrategy("No pref_ccm key found in icc profile")
        return str(pref_ccm.value.decode("ascii").rstrip(' \0'))


class ColorSpaceOJPCheck(AbsColorSpaceExtractor):
    """Color space extractor using openjpeg library."""

    def check(self, image: str) -> str:
        """Check the color space of a given file.

        Args:
            image:
                path to an image file

        Returns:
            color space name

        """
        return openjp2wrap.get_colorspace(image)
