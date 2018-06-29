import os

import pytest

from uiucprescon import imagevalidate
from uiucprescon.imagevalidate import profiles
from uiucprescon.imagevalidate import IssueCategory

TEST_PATH = os.path.join(os.path.dirname(__file__), "henrytestmetadata")


@pytest.mark.integration
def test_bitdepth():
    test_image = os.path.join(TEST_PATH, "bitdepth", "0000001.tif")
    hathi_tiff_profile = imagevalidate.Profile(profiles.HathiTiff())
    report = hathi_tiff_profile.validate(file=test_image)
    print(report)
    assert len(report.issues()) == 1
    assert len(report.issues(issue_type=IssueCategory.INVALID_DATA)) == 1
    assert not report.valid


@pytest.mark.integration
def test_colorspace():
    test_image = os.path.join(TEST_PATH, "colorspace", "0000001.tif")
    hathi_tiff_profile = imagevalidate.Profile(profiles.HathiTiff())
    report = hathi_tiff_profile.validate(file=test_image)
    print(report)
    assert len(report.issues()) == 1
    assert len(report.issues(issue_type=IssueCategory.INVALID_DATA)) == 1
    assert len(report.issues(issue_type=IssueCategory.EMPTY_DATA)) == 0
    assert len(report.issues(issue_type=IssueCategory.MISSING_FIELD)) == 0
    assert not report.valid


@pytest.mark.integration
def test_correct():
    test_image = os.path.join(TEST_PATH, "correct", "0000001.tif")
    hathi_tiff_profile = imagevalidate.Profile(profiles.HathiTiff())
    report = hathi_tiff_profile.validate(file=test_image)
    print(report)
    assert "No issues discovered" in str(report)
    assert len(report.issues()) == 0
    assert len(report.issues(issue_type=IssueCategory.INVALID_DATA)) == 0
    assert len(report.issues(issue_type=IssueCategory.EMPTY_DATA)) == 0
    assert len(report.issues(issue_type=IssueCategory.MISSING_FIELD)) == 0
    assert report.valid


@pytest.mark.integration
def test_empty_address():
    test_image = os.path.join(TEST_PATH, "empty_address", "0000001.tif")
    hathi_tiff_profile = imagevalidate.Profile(profiles.HathiTiff())
    report = hathi_tiff_profile.validate(file=test_image)
    print(report)
    assert len(report.issues()) == 1
    assert len(report.issues(issue_type=IssueCategory.INVALID_DATA)) == 0
    assert len(report.issues(issue_type=IssueCategory.EMPTY_DATA)) == 1
    assert len(report.issues(issue_type=IssueCategory.MISSING_FIELD)) == 0
    assert not report.valid


@pytest.mark.integration
def test_empty_city():
    test_image = os.path.join(TEST_PATH, "empty_city", "0000001.tif")
    hathi_tiff_profile = imagevalidate.Profile(profiles.HathiTiff())
    report = hathi_tiff_profile.validate(file=test_image)
    assert len(report.issues(issue_type=IssueCategory.INVALID_DATA)) == 0
    assert len(report.issues(issue_type=IssueCategory.EMPTY_DATA)) == 1
    assert len(report.issues(issue_type=IssueCategory.MISSING_FIELD)) == 0
    print(report)
    assert len(report.issues()) == 1
    assert not report.valid


@pytest.mark.integration
def test_empty_country():
    test_image = os.path.join(TEST_PATH, "empty_country", "0000001.tif")
    hathi_tiff_profile = imagevalidate.Profile(profiles.HathiTiff())
    report = hathi_tiff_profile.validate(file=test_image)
    print(report)
    assert len(report.issues()) == 1
    assert len(report.issues(issue_type=IssueCategory.INVALID_DATA)) == 0
    assert len(report.issues(issue_type=IssueCategory.EMPTY_DATA)) == 1
    assert len(report.issues(issue_type=IssueCategory.MISSING_FIELD)) == 0
    assert not report.valid


@pytest.mark.integration
def test_missing_creator():
    test_image = os.path.join(TEST_PATH, "missing_creator", "0000001.tif")
    hathi_tiff_profile = imagevalidate.Profile(profiles.HathiTiff())
    report = hathi_tiff_profile.validate(file=test_image)
    print(report)
    assert len(report.issues()) == 1
    assert len(report.issues(issue_type=IssueCategory.INVALID_DATA)) == 0
    assert len(report.issues(issue_type=IssueCategory.EMPTY_DATA)) == 0
    assert len(report.issues(issue_type=IssueCategory.MISSING_FIELD)) == 1
    assert not report.valid


@pytest.mark.integration
def test_empty_state():
    test_image = os.path.join(TEST_PATH, "empty_state", "0000001.tif")
    hathi_tiff_profile = imagevalidate.Profile(profiles.HathiTiff())
    report = hathi_tiff_profile.validate(file=test_image)
    assert len(report.issues()) == 1
    assert len(report.issues(issue_type=IssueCategory.INVALID_DATA)) == 0
    assert len(report.issues(issue_type=IssueCategory.EMPTY_DATA)) == 1
    assert len(report.issues(issue_type=IssueCategory.MISSING_FIELD)) == 0
    print(report)
    assert not report.valid


@pytest.mark.integration
def test_empty_zip():
    test_image = os.path.join(TEST_PATH, "empty_zip", "0000001.tif")
    hathi_tiff_profile = imagevalidate.Profile(profiles.HathiTiff())
    report = hathi_tiff_profile.validate(file=test_image)
    print(report)
    assert len(report.issues()) == 1
    assert len(report.issues(issue_type=IssueCategory.INVALID_DATA)) == 0
    assert len(report.issues(issue_type=IssueCategory.EMPTY_DATA)) == 1
    assert len(report.issues(issue_type=IssueCategory.MISSING_FIELD)) == 0
    assert not report.valid


@pytest.mark.integration
def test_empty_phonenumber():
    test_image = os.path.join(TEST_PATH, "empty_phonenumber", "0000001.tif")
    hathi_tiff_profile = imagevalidate.Profile(profiles.HathiTiff())
    report = hathi_tiff_profile.validate(file=test_image)
    print(report)
    assert len(report.issues()) == 1
    assert len(report.issues(issue_type=IssueCategory.INVALID_DATA)) == 0
    assert len(report.issues(issue_type=IssueCategory.EMPTY_DATA)) == 1
    assert len(report.issues(issue_type=IssueCategory.MISSING_FIELD)) == 0
    assert not report.valid


@pytest.mark.integration
def test_pixelarray():

    test_image = os.path.join(TEST_PATH, "pixelarray", "0000001.tif")
    hathi_tiff_profile = imagevalidate.Profile(profiles.HathiTiff())
    report = hathi_tiff_profile.validate(file=test_image)
    print(report)
    assert len(report.issues()) == 1
    assert len(report.issues(issue_type=IssueCategory.INVALID_DATA)) == 1
    assert len(report.issues(issue_type=IssueCategory.EMPTY_DATA)) == 0
    assert len(report.issues(issue_type=IssueCategory.MISSING_FIELD)) == 0
    assert not report.valid
