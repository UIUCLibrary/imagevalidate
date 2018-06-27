import os

import pytest

from uiucprescon import imagevalidate
from uiucprescon.imagevalidate import profiles

TEST_PATH = "T:/HenryTest-PSR_2/DCC/henrytestmetadata"


@pytest.mark.integration
def test_bitdepth():
    test_image = os.path.join(TEST_PATH, "bitdepth", "0000001.tif")
    hathi_tiff_profile = imagevalidate.Profile(profiles.HathiTiff())
    report = hathi_tiff_profile.validate(file=test_image)
    print(report)
    assert len(report.issues()) == 1
    assert len(report.issues(issue_type="mismatch")) == 1
    assert not report.valid


@pytest.mark.integration
def test_colorspace():
    test_image = os.path.join(TEST_PATH, "colorspace", "0000001.tif")
    hathi_tiff_profile = imagevalidate.Profile(profiles.HathiTiff())
    report = hathi_tiff_profile.validate(file=test_image)
    assert len(report.issues()) == 1
    assert len(report.issues(issue_type="mismatch")) == 1
    assert len(report.issues(issue_type="empty")) == 0
    assert len(report.issues(issue_type="missing")) == 0
    assert not report.valid


@pytest.mark.integration
def test_correct():
    test_image = os.path.join(TEST_PATH, "correct", "0000001.tif")
    hathi_tiff_profile = imagevalidate.Profile(profiles.HathiTiff())
    report = hathi_tiff_profile.validate(file=test_image)
    print(report)
    assert len(report.issues()) == 0
    assert len(report.issues(issue_type="mismatch")) == 0
    assert len(report.issues(issue_type="empty")) == 0
    assert len(report.issues(issue_type="missing")) == 0
    assert report.valid


@pytest.mark.integration
def test_missingaddress():
    test_image = os.path.join(TEST_PATH, "missingaddress", "0000001.tif")
    hathi_tiff_profile = imagevalidate.Profile(profiles.HathiTiff())
    report = hathi_tiff_profile.validate(file=test_image)
    print(report)
    assert len(report.issues()) == 1
    assert len(report.issues(issue_type="mismatch")) == 0
    assert len(report.issues(issue_type="empty")) == 1
    assert len(report.issues(issue_type="missing")) == 0
    assert not report.valid


@pytest.mark.integration
def test_missingcity():
    test_image = os.path.join(TEST_PATH, "missingcity", "0000001.tif")
    hathi_tiff_profile = imagevalidate.Profile(profiles.HathiTiff())
    report = hathi_tiff_profile.validate(file=test_image)
    assert len(report.issues(issue_type="mismatch")) == 0
    assert len(report.issues(issue_type="empty")) == 1
    assert len(report.issues(issue_type="missing")) == 0
    print(report)
    assert len(report.issues()) == 1
    assert not report.valid


@pytest.mark.integration
def test_missingcountry():
    test_image = os.path.join(TEST_PATH, "missingcountry", "0000001.tif")
    hathi_tiff_profile = imagevalidate.Profile(profiles.HathiTiff())
    report = hathi_tiff_profile.validate(file=test_image)
    print(report)
    assert len(report.issues()) == 1
    assert len(report.issues(issue_type="mismatch")) == 0
    assert len(report.issues(issue_type="empty")) == 1
    assert len(report.issues(issue_type="missing")) == 0
    assert not report.valid


@pytest.mark.integration
def test_missingcreator():
    test_image = os.path.join(TEST_PATH, "missingcreator", "0000001.tif")
    hathi_tiff_profile = imagevalidate.Profile(profiles.HathiTiff())
    report = hathi_tiff_profile.validate(file=test_image)
    print(report)
    assert len(report.issues()) == 1
    assert len(report.issues(issue_type="mismatch")) == 0
    assert len(report.issues(issue_type="empty")) == 0
    assert len(report.issues(issue_type="missing")) == 1
    assert not report.valid


@pytest.mark.integration
def test_missingstate():
    test_image = os.path.join(TEST_PATH, "missingstate", "0000001.tif")
    hathi_tiff_profile = imagevalidate.Profile(profiles.HathiTiff())
    report = hathi_tiff_profile.validate(file=test_image)
    assert len(report.issues()) == 1
    assert len(report.issues(issue_type="mismatch")) == 0
    assert len(report.issues(issue_type="empty")) == 1
    assert len(report.issues(issue_type="missing")) == 0
    print(report)
    assert not report.valid


@pytest.mark.integration
def test_missingzip():
    test_image = os.path.join(TEST_PATH, "missingzip", "0000001.tif")
    hathi_tiff_profile = imagevalidate.Profile(profiles.HathiTiff())
    report = hathi_tiff_profile.validate(file=test_image)
    print(report)
    assert len(report.issues()) == 1
    assert len(report.issues(issue_type="mismatch")) == 0
    assert len(report.issues(issue_type="empty")) == 1
    assert len(report.issues(issue_type="missing")) == 0
    assert not report.valid


@pytest.mark.integration
def test_phonenumber():
    test_image = os.path.join(TEST_PATH, "phonenumber", "0000001.tif")
    hathi_tiff_profile = imagevalidate.Profile(profiles.HathiTiff())
    report = hathi_tiff_profile.validate(file=test_image)
    print(report)
    assert len(report.issues()) == 1
    assert len(report.issues(issue_type="mismatch")) == 0
    assert len(report.issues(issue_type="empty")) == 1
    assert len(report.issues(issue_type="missing")) == 0
    assert not report.valid


@pytest.mark.integration
def test_pixelarray():

    test_image = os.path.join(TEST_PATH, "pixelarray", "0000001.tif")
    hathi_tiff_profile = imagevalidate.Profile(profiles.HathiTiff())
    report = hathi_tiff_profile.validate(file=test_image)
    print(report)
    assert len(report.issues()) == 1
    assert len(report.issues(issue_type="mismatch")) == 0
    assert len(report.issues(issue_type="empty")) == 1
    assert len(report.issues(issue_type="missing")) == 0
    assert not report.valid
