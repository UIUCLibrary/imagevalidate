import pytest
from uiucprescon.imagevalidate import profiles
from uiucprescon import imagevalidate

import os


def test_loaded():
    assert imagevalidate.__name__


def test_load_profile():
    hathi_jp2_profile = imagevalidate.Profile(profiles.HathiJP2())
    assert hathi_jp2_profile is not None


def test_missing_file():
    hathi_jp2_profile = imagevalidate.Profile(profiles.HathiJP2())
    with pytest.raises(FileNotFoundError):
        report = hathi_jp2_profile.validate(file="invalid_file.jp2")


if "test_image" in os.environ.keys():
    def test_report():
        test_image = os.environ["test_image"]
        assert os.path.exists(test_image)
        hathi_jp2_profile = imagevalidate.Profile(profiles.HathiJP2())
        report = hathi_jp2_profile.validate(file=test_image)
        assert isinstance(report, imagevalidate.Report)
        assert report.valid

