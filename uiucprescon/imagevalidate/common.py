import abc

import py3exiv2bind
import py3exiv2bind.core


class InvalidStrategy(Exception):
    pass


class AbsColorSpaceExtractor(metaclass=abc.ABCMeta):
    """Base class for different methods of extracting the color space from an \
    image file"""

    def check(self, image: str) -> str:
        pass


class ExtractColorSpace:
    def __init__(self, strategy: AbsColorSpaceExtractor) -> None:
        self.strategy = strategy

    def check(self, image: str):
        return self.strategy.check(image)


class ColorSpaceIccDeviceModelCheck(AbsColorSpaceExtractor):
    """Extract the color space by trying to read the device_model tag in the
    ICC profile.
    Useful for identifying sRGB."""

    def check(self, image: py3exiv2bind.Image) -> str:
        try:
            icc = image.icc()
        except py3exiv2bind.core.NoICCError as e:
            raise InvalidStrategy("Unable to get ICC profile.")

        device_model = icc.get('device_model').value \
            .decode("ascii").rstrip(' \0')
        if not device_model:
            raise InvalidStrategy("No device_model key found in icc profile")
        return str(device_model)


class ColorSpaceIccPrefCcmCheck(AbsColorSpaceExtractor):
    """Extract the color space value by reading the pref_ccm from the header
    of the ICC profile."""

    def check(self, image: py3exiv2bind.Image) -> str:
        try:
            icc = image.icc()
        except py3exiv2bind.core.NoICCError as e:
            raise InvalidStrategy("Unable to get ICC profile."
                                  "Reason: {}".format(e))

        pref_ccm = icc.get("pref_ccm").value.decode("ascii").rstrip(' \0')
        if not pref_ccm:
            raise InvalidStrategy("No pref_ccm key found in icc profile")
        return str(pref_ccm)