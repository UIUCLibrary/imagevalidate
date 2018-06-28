import collections

import py3exiv2bind
import typing
from uiucprescon.imagevalidate import IssueCategory
from uiucprescon.imagevalidate import Report
from uiucprescon.imagevalidate.report import Result
from . import AbsProfile


class HathiTiff(AbsProfile):
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

    def validate(self, file: str) -> Report:
        report = Report()
        report.filename = file
        image = py3exiv2bind.Image(file)
        report_data = self.get_data_from_image(image)
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
    def get_data_from_image(cls, image: py3exiv2bind.Image) \
            -> typing.Dict[str, Result]:

        data = super().get_data_from_image(image)

        color_space = cls.determine_color_space(image)
        data['Color Space'] = Result(expected="sRGB", actual=color_space)

        longest_side = max(image.pixelHeight, image.pixelWidth)

        data['Pixel on longest angle'] = Result(
            expected="3000",
            actual=str(longest_side)
        )

        return data

    @staticmethod
    def determine_color_space(image: py3exiv2bind.Image)->typing.Optional[str]:
        icc = image.icc()

        device_model = icc.get('device_model')\
            .value.decode("ascii").rstrip(' \0')

        if device_model:
            return device_model

        pref_ccm = icc.get("pref_ccm").value.decode("ascii").rstrip(' \0')
        if pref_ccm:
            return pref_ccm

        return None
