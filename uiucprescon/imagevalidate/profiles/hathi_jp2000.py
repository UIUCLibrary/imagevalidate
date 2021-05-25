"""Profile for HathiTrust tiff files."""

import collections
import sys

import py3exiv2bind
import typing
from uiucprescon.imagevalidate import IssueCategory, common
from uiucprescon.imagevalidate import Report
from uiucprescon.imagevalidate.report import Result
from uiucprescon.imagevalidate import openjp2wrap
from . import AbsProfile


class HathiJP2000(AbsProfile):
    """Profile for validating .jp2 files for HathiTrust."""

    expected_metadata_any_value = [
        'Xmp.dc.creator',

        # Address
        'Xmp.iptc.CreatorContactInfo/Iptc4xmpCore:CiAdrExtadr',

        # City
        'Xmp.iptc.CreatorContactInfo/Iptc4xmpCore:CiAdrCity',

        # State
        'Xmp.iptc.CreatorContactInfo/Iptc4xmpCore:CiAdrRegion',

        # Zip code
        'Xmp.iptc.CreatorContactInfo/Iptc4xmpCore:CiAdrPcode',

        # Country
        'Xmp.iptc.CreatorContactInfo/Iptc4xmpCore:CiAdrCtry',

        # phone number
        'Xmp.iptc.CreatorContactInfo/Iptc4xmpCore:CiTelWork',
    ]

    expected_metadata_constants = {
        "Exif.Image.XResolution": "400/1",
        "Exif.Image.YResolution": "400/1",
    }
    valid_extensions = {".jp2"}

    @staticmethod
    def profile_name() -> str:
        """Get the profile name."""
        return "HathiTrust JPEG 2000"

    def validate(self, file: str) -> Report:
        """Validate the image file as a HathiTrust jpeg2000 image.

        Args:
            file:
                File path to an image file

        Returns:
            Returns a report of the results.

        """
        report = Report()
        report.filename = file
        report_data = self.get_data_from_image(file)
        report._properties = report_data

        analysis: typing.Dict[IssueCategory, list] = \
            collections.defaultdict(list)

        for key, result in report_data.items():
            issue_category = self.analyze_data_for_issues(result)
            if issue_category:
                message = self.generate_error_msg(issue_category, key, result)
                analysis[issue_category].append(message)

        report._data.update(analysis)

        return report

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
