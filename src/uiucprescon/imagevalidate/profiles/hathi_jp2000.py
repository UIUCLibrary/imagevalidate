"""Profile for HathiTrust tiff files."""

import sys
import typing

import py3exiv2bind
from uiucprescon.imagevalidate import common
from uiucprescon.imagevalidate.report import Result
from uiucprescon.imagevalidate import openjp2wrap  # type: ignore
from . import hathi_common


class HathiJP2000(hathi_common.AbsValidateHathiTrustProfile):
    """Profile for validating .jp2 files for HathiTrust."""

    expected_metadata_any_value =\
        hathi_common.SHARED_EXPECTED_METADATA_ANY_VALUE

    expected_metadata_constants =\
        hathi_common.SHARED_EXPECT_RESOLUTION_CONSTANTS

    valid_extensions = {".jp2"}

    @staticmethod
    def profile_name() -> str:
        """Get the profile name."""
        return "HathiTrust JPEG 2000"

    @classmethod
    def get_data_from_image(cls, filename: str) \
            -> typing.Dict[str, Result]:
        """Get data from image."""
        image = py3exiv2bind.Image(filename)
        data = super().get_data_from_image(filename)

        # Currently unable to properly extract enumerated color space
        #
        color_space = cls.determine_color_space(filename)
        if color_space:
            data['Color Space'] = Result(expected="sRGB", actual=color_space)
        else:
            data['Color Space'] = Result(expected="sRGB",
                                         actual="Unknown")

        longest_side = max(image.pixelHeight, image.pixelWidth)

        data['Pixel on longest angle'] = Result(
            expected="3000",
            actual=str(longest_side)
        )

        data['color bit depth'] = Result(
            expected="8",
            actual=str(openjp2wrap.get_bit_depth(filename))
        )

        return data

    @staticmethod
    def determine_color_space(image: str) -> typing.Optional[str]:
        """Determine the color space of a given file.

        Args:
            filename:
                file path to image

        Returns:
            color space name

        """
        strategies = [
            common.ColorSpaceIccDeviceModelCheck(),
            common.ColorSpaceIccPrefCcmCheck(),
            common.ColorSpaceOJPCheck()

        ]
        for strategy in strategies:

            try:
                colorspace_extractor = common.ExtractColorSpace(strategy)
                return colorspace_extractor.check(image)
            except common.InvalidStrategy as error:
                print(f"Unable to determine colorspace using "
                      f"{strategy.__class__.__name__}. Reason given: {error}",
                      file=sys.stderr)
        return None
