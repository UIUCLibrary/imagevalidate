import abc
import sys

import py3exiv2bind
import typing
from uiucprescon.imagevalidate import Report, common
from uiucprescon.imagevalidate.report import Result
from . import AbsProfile


class AbsHathiTiff(AbsProfile):
    """Abstract baseclass for Profile for validating Tiff files for
    HathiTrust"""

    valid_extensions = {".tif"}

    # These strategy are ordered in fastest to slowest
    colospacer_lookup_strategies = [
            common.ColorSpaceIccDeviceModelCheck,
            common.ColorSpaceIccPrefCcmCheck,
        ]

    def validate(self, file: str) -> Report:
        report = Report()
        report.filename = file
        report_data = self.get_data_from_image(file)
        report._properties = report_data

        analysis = self.analyze(report_data)

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

        for strategy in AbsHathiTiff.colospacer_lookup_strategies:
            try:
                colorspace_extractor = common.ExtractColorSpace(strategy())
                return colorspace_extractor.check(filename)
            except common.InvalidStrategy as e:
                print(f"Unable to determine color space using "
                      f"{strategy.__name__}. Reason given: {e}",
                      file=sys.stderr)
        return None

    @staticmethod
    @abc.abstractmethod
    def profile_name() -> str:
        raise NotImplementedError()


class HathiTiffUiuc(AbsHathiTiff):
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
        "Exif.Image.SamplesPerPixel": "3",
    }
    @staticmethod
    def profile_name() -> str:
        return "HathiTrust Tiff"


class HathiTiffContoneBase(AbsHathiTiff):
    expected_metadata_constants = {
        "Exif.Image.XResolution": "400/1",
        "Exif.Image.YResolution": "400/1",
    }

    @staticmethod
    @abc.abstractmethod
    def profile_name() -> str:
        raise NotImplementedError()


class HathiTiffRGB(HathiTiffContoneBase):
    expected_metadata_constants = \
        HathiTiffContoneBase.expected_metadata_constants.copy()

    expected_metadata_constants['Exif.Image.BitsPerSample'] = "8 8 8"
    expected_metadata_constants["Exif.Image.SamplesPerPixel"] = "3"

    ignored_metadata_fields = [
        "Exif.Image.InterColorProfile"
    ]

    @staticmethod
    def profile_name() -> str:
        return "HathiTrust Contone Tiff RGB"


class HathiTiffGreyscale(HathiTiffContoneBase):
    expected_metadata_constants = \
        HathiTiffContoneBase.expected_metadata_constants.copy()

    expected_metadata_constants['Exif.Image.BitsPerSample'] = "8"
    expected_metadata_constants["Exif.Image.SamplesPerPixel"] = "1"
    expected_metadata_constants["Exif.Image.Orientation"] = "1"

    expected_metadata_no_value = [
        "Exif.Image.InterColorProfile"
    ]
    @staticmethod
    def profile_name() -> str:
        return "HathiTrust Contone Tiff Greyscale"


class HathiTiffBitone(AbsHathiTiff):
    expected_metadata_constants = {
        "Exif.Image.XResolution": "600/1",
        "Exif.Image.YResolution": "600/1",
        'Exif.Image.BitsPerSample': "1",
        "Exif.Image.SamplesPerPixel": "1",
        "Exif.Image.Orientation": "1",
    }

    @staticmethod
    @abc.abstractmethod
    def profile_name() -> str:
        return "HathiTrust Bitone"
