"""Profile for HathiTrust tiff files."""

from __future__ import annotations

import sys
import typing

import py3exiv2bind
from uiucprescon.imagevalidate import common
from uiucprescon.imagevalidate.report import Result
from . import hathi_common


class HathiTiff(hathi_common.AbsValidateHathiTrustProfile):
    """Profile for validating Tiff files for HathiTrust."""

    expected_metadata_any_value =\
        hathi_common.SHARED_EXPECTED_METADATA_ANY_VALUE

    expected_metadata_constants = \
        {
            **hathi_common.SHARED_EXPECT_RESOLUTION_CONSTANTS,
            **{
                'Exif.Image.BitsPerSample': "8 8 8",
            }
        }
    valid_extensions = {".tif"}

    @staticmethod
    def profile_name() -> str:
        """Get the profile name."""
        return "HathiTrust Tiff"

    @classmethod
    def get_data_from_image(cls, filename: str) -> typing.Dict[str, Result]:
        """Get data from image."""
        image = py3exiv2bind.Image(filename)
        data = super().get_data_from_image(filename)

        color_space = cls.determine_color_space(filename)
        data['Color Space'] = Result(expected="sRGB", actual=color_space)

        longest_side = max(image.pixelHeight, image.pixelWidth)

        data['Pixel on longest angle'] = Result(
            expected="3000",
            actual=str(longest_side)
        )

        return data

    @staticmethod
    def determine_color_space(filename: str) -> typing.Optional[str]:
        """Determine the color space of a given file.

        Args:
            filename:
                file path to image

        Returns:
            color space name

        """
        strategies = [
            common.ColorSpaceIccDeviceModelCheck,
            common.ColorSpaceIccPrefCcmCheck,

        ]
        for strategy in strategies:
            try:
                colorspace_extractor = common.ExtractColorSpace(strategy())
                return colorspace_extractor.check(filename)
            except common.InvalidStrategy as error:
                print(f"Unable to determine color space using "
                      f"{strategy.__name__}. Reason given: {error}",
                      file=sys.stderr)
        return None
