import collections

import py3exiv2bind
import typing
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
        report_data = self._get_report_data(image)
        report._properties = report_data
        analysis = self.analyze_data(report_data)

        for issue in self.parse_issues(analysis, report_data):
            report._issues.append(issue)

        return report

    @classmethod
    def _get_report_data(cls, image: py3exiv2bind.Image) \
            -> typing.Dict[str, Result]:

        data: typing.Dict[str, Result] = dict()

        data.update(cls._get_metadata_has_values(image))
        data.update(cls._get_metadata_static_values(image))

        color_space = cls.determine_color_space(image)
        data['Color Space'] = Result(expected="sRGB", actual=color_space)

        return data

    @classmethod
    def determine_color_space(cls, image):
        icc = image.icc()
        device_model = icc.get('device_model')
        if device_model:
            color_space = str(device_model)
        else:
            color_space = None
        return color_space

    @staticmethod
    def analyze_data(data: typing.Dict[str, Result]) -> \
            typing.Dict[str, list]:

        analysis: typing.Dict[str, list] = collections.defaultdict(list)
        for field, result in data.items():
            if result.actual is None:
                analysis["missing"].append(field)
                continue

            if result.actual != result.expected and \
                    result.expected is not None:

                analysis["mismatch"].append(field)

        return dict(analysis)
