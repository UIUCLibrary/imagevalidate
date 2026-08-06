"""Shared values for HathiTrust profiles."""
from __future__ import annotations

import collections
import typing
from abc import ABC

from uiucprescon.imagevalidate import Report
from . import AbsProfile

if typing.TYPE_CHECKING:
    from uiucprescon.imagevalidate import IssueCategory

__all__ = [
    "SHARED_EXPECTED_METADATA_ANY_VALUE",
    "SHARED_EXPECT_RESOLUTION_CONSTANTS"
]

SHARED_EXPECTED_METADATA_ANY_VALUE = [
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

SHARED_EXPECT_RESOLUTION_CONSTANTS = {
    "Exif.Image.XResolution": "400/1",
    "Exif.Image.YResolution": "400/1",
}


class AbsValidateHathiTrustProfile(AbsProfile, ABC):
    """Profile for validating files for HathiTrust."""

    def validate(self, file: str) -> Report:
        """Validate the image file as a HathiTrust image.

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
