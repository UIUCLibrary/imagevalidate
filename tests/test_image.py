import pytest
from uiucprescon.imagevalidate import profiles
from uiucprescon import imagevalidate


def test_loaded():
    assert imagevalidate.__name__


def test_load_profile():
    hathi_tiff_profile = imagevalidate.Profile(profiles.HathiTiffUiuc())
    assert isinstance(hathi_tiff_profile, imagevalidate.Profile)


def test_missing_file():
    hathi_tiff_profile = imagevalidate.Profile(profiles.HathiTiffUiuc())
    with pytest.raises(FileNotFoundError):
        hathi_tiff_profile.validate(file="invalid_file.tif")

