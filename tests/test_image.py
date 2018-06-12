import pytest
from uiucprescon import imagevalidate
from uiucprescon.imagevalidate import profiles


def test_loaded():
    assert imagevalidate.__name__


def test_load_profile():
    hathi_jp2_profile = imagevalidate.Profile(profiles.HathiJP2())
    assert hathi_jp2_profile is not None


def test_missing_file():
    hathi_jp2_profile = imagevalidate.Profile(profiles.HathiJP2())
    with pytest.raises(FileNotFoundError):
        report = hathi_jp2_profile.validate(file="invalid_file.jp2")

