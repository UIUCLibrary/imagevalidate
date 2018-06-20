import os

import pytest

from uiucprescon import imagevalidate
from uiucprescon.imagevalidate import profiles


def get_test_tiff_file():
    return os.path.join(os.path.dirname(__file__), "00000030.tif")


@pytest.mark.integration
def test_hathi_tiff():

    test_image = get_test_tiff_file()
    assert os.path.exists(test_image)
    hathi_tiff_profile = imagevalidate.Profile(profiles.HathiTiff())
    report = hathi_tiff_profile.validate(file=test_image)
    print(report)
    assert isinstance(report, imagevalidate.Report)
    assert report.valid