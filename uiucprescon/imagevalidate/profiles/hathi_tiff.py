import collections
import sys

import py3exiv2bind
import typing
from uiucprescon.imagevalidate import IssueCategory
from uiucprescon.imagevalidate import Report, common
from uiucprescon.imagevalidate.report import Result
from . import AbsProfile


class HathiTiff(AbsProfile):
    """Profile for validating Tiff files for HathiTrust"""
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
        'Exif.Image.BitsPerSample': "8 8 8",
    }
    valid_extensions = {".tif"}

    @staticmethod
    def profile_name() -> str:
        return "HathiTrust Tiff"

    def validate(self, file: str) -> Report:
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
    def get_data_from_image(cls, filename: str) -> typing.Dict[str, Result]:

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
        strategies = [
            common.ColorSpaceIccDeviceModelCheck,
            common.ColorSpaceIccPrefCcmCheck,

        ]
        for strategy in strategies:
            try:
                colorspace_extractor = common.ExtractColorSpace(strategy())
                return colorspace_extractor.check(filename)
            except common.InvalidStrategy as e:
                print(f"Unable to determine color space using "
                      f"{strategy.__name__}. Reason given: {e}",
                      file=sys.stderr)
        return None
