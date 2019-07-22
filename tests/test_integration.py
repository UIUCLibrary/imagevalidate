import os
import shutil

import pytest

from uiucprescon import imagevalidate
from uiucprescon.imagevalidate import IssueCategory
import os


@pytest.mark.integration
@pytest.mark.parametrize("test_file,profile_name", [
    (os.path.join("bitdepth", "0000001.tif"), "HathiTrust Tiff"),
    (os.path.join("bitdepth", "0000001.jp2"), "HathiTrust JPEG 2000"),
])
def test_bitdepth(sample_data, test_file, profile_name):
    test_image = os.path.join(sample_data, test_file)
    profile_type = imagevalidate.get_profile(profile_name)
    hathi_tiff_profile = imagevalidate.Profile(profile_type)
    report = hathi_tiff_profile.validate(file=test_image)
    print(report)
    assert len(report.issues()) == 1
    assert len(report.issues(issue_type=IssueCategory.INVALID_DATA)) == 1
    assert not report.valid


@pytest.mark.integration
@pytest.mark.parametrize("test_file,profile_name", [
    (os.path.join("colorspace", "0000001.tif"), "HathiTrust Tiff"),
    # (os.path.join("colorspace", "0000001.jp2"), "HathiTrust JPEG 2000"),
])
def test_invalid_colorspace(sample_data, test_file, profile_name):
    test_image = os.path.join(sample_data, test_file)
    profile_type = imagevalidate.get_profile(profile_name)
    hathi_tiff_profile = imagevalidate.Profile(profile_type)
    report = hathi_tiff_profile.validate(file=test_image)
    print(report)
    assert len(report.issues()) == 1
    assert len(report.issues(issue_type=IssueCategory.INVALID_DATA)) == 1
    assert len(report.issues(issue_type=IssueCategory.EMPTY_DATA)) == 0
    assert len(report.issues(issue_type=IssueCategory.MISSING_FIELD)) == 0
    assert not report.valid
    assert report._properties['Color Space'].actual != "Unknown"


@pytest.mark.integration
@pytest.mark.parametrize("test_file,profile_name", [
    (os.path.join("colorspace", "0000001.jp2"), "HathiTrust JPEG 2000"),
])
def test_valid_colorspace(sample_data, test_file, profile_name):
    test_image = os.path.join(sample_data, test_file)
    profile_type = imagevalidate.get_profile(profile_name)
    validation_profile = imagevalidate.Profile(profile_type)
    report = validation_profile.validate(file=test_image)
    print(report)
    assert len(report.issues()) == 0
    assert len(report.issues(issue_type=IssueCategory.INVALID_DATA)) == 0
    assert len(report.issues(issue_type=IssueCategory.EMPTY_DATA)) == 0
    assert len(report.issues(issue_type=IssueCategory.MISSING_FIELD)) == 0
    assert report.valid
    assert report._properties['Color Space'].actual == "sRGB"


@pytest.mark.integration
@pytest.mark.parametrize("test_file,profile_name", [
    (os.path.join("correct", "0000001.tif"), "HathiTrust Tiff"),
    (os.path.join("correct", "0000001.jp2"), "HathiTrust JPEG 2000"),
])
def test_correct(sample_data, test_file, profile_name):
    test_image = os.path.join(sample_data, test_file)
    profile_type = imagevalidate.get_profile(profile_name)
    hathi_tiff_profile = imagevalidate.Profile(profile_type)
    report = hathi_tiff_profile.validate(file=test_image)
    print(report)
    assert "No issues discovered" in str(report)
    assert len(report.issues()) == 0
    assert len(report.issues(issue_type=IssueCategory.INVALID_DATA)) == 0
    assert len(report.issues(issue_type=IssueCategory.EMPTY_DATA)) == 0
    assert len(report.issues(issue_type=IssueCategory.MISSING_FIELD)) == 0
    assert report.valid


@pytest.mark.integration
@pytest.mark.parametrize("test_file,profile_name", [
    (os.path.join("empty_address", "0000001.tif"), "HathiTrust Tiff"),
    (os.path.join("empty_address", "0000001.jp2"), "HathiTrust JPEG 2000"),
])
def test_empty_address(sample_data, test_file, profile_name):
    test_image = os.path.join(sample_data, test_file)
    profile_type = imagevalidate.get_profile(profile_name)
    hathi_tiff_profile = imagevalidate.Profile(profile_type)
    report = hathi_tiff_profile.validate(file=test_image)
    print(report)
    assert len(report.issues()) == 1
    assert len(report.issues(issue_type=IssueCategory.INVALID_DATA)) == 0
    assert len(report.issues(issue_type=IssueCategory.EMPTY_DATA)) == 1
    assert len(report.issues(issue_type=IssueCategory.MISSING_FIELD)) == 0
    assert not report.valid


@pytest.mark.integration
@pytest.mark.parametrize("test_file,profile_name", [
    (os.path.join("empty_city", "0000001.tif"), "HathiTrust Tiff"),
    (os.path.join("empty_city", "0000001.jp2"), "HathiTrust JPEG 2000"),
])
def test_empty_city(sample_data, test_file, profile_name):
    test_image = os.path.join(sample_data, test_file)
    profile_type = imagevalidate.get_profile(profile_name)
    hathi_tiff_profile = imagevalidate.Profile(profile_type)
    report = hathi_tiff_profile.validate(file=test_image)
    assert len(report.issues(issue_type=IssueCategory.INVALID_DATA)) == 0
    assert len(report.issues(issue_type=IssueCategory.EMPTY_DATA)) == 1
    assert len(report.issues(issue_type=IssueCategory.MISSING_FIELD)) == 0
    print(report)
    assert len(report.issues()) == 1
    assert not report.valid


@pytest.mark.integration
@pytest.mark.parametrize("test_file,profile_name", [
    (os.path.join("empty_country", "0000001.tif"), "HathiTrust Tiff"),
    (os.path.join("empty_country", "0000001.jp2"), "HathiTrust JPEG 2000"),
])
def test_empty_country(sample_data, test_file, profile_name):
    test_image = os.path.join(sample_data, test_file)
    profile_type = imagevalidate.get_profile(profile_name)
    hathi_tiff_profile = imagevalidate.Profile(profile_type)
    report = hathi_tiff_profile.validate(file=test_image)
    print(report)
    assert len(report.issues()) == 1
    assert len(report.issues(issue_type=IssueCategory.INVALID_DATA)) == 0
    assert len(report.issues(issue_type=IssueCategory.EMPTY_DATA)) == 1
    assert len(report.issues(issue_type=IssueCategory.MISSING_FIELD)) == 0
    assert not report.valid


@pytest.mark.integration
@pytest.mark.parametrize("test_file,profile_name", [
    (os.path.join("missing_creator", "0000001.tif"), "HathiTrust Tiff"),
    (os.path.join("missing_creator", "0000001.jp2"), "HathiTrust JPEG 2000"),
])
def test_missing_creator(sample_data, test_file, profile_name):
    test_image = os.path.join(sample_data, test_file)
    profile_type = imagevalidate.get_profile(profile_name)
    hathi_tiff_profile = imagevalidate.Profile(profile_type)
    report = hathi_tiff_profile.validate(file=test_image)
    print(report)
    assert len(report.issues()) == 1
    assert len(report.issues(issue_type=IssueCategory.INVALID_DATA)) == 0
    assert len(report.issues(issue_type=IssueCategory.EMPTY_DATA)) == 0
    assert len(report.issues(issue_type=IssueCategory.MISSING_FIELD)) == 1
    assert not report.valid


@pytest.mark.integration
@pytest.mark.parametrize("test_file,profile_name", [
    (os.path.join("empty_state", "0000001.tif"), "HathiTrust Tiff"),
    (os.path.join("empty_state", "0000001.jp2"), "HathiTrust JPEG 2000"),
])
def test_empty_state(sample_data, test_file, profile_name):
    test_image = os.path.join(sample_data, test_file)
    profile_type = imagevalidate.get_profile(profile_name)
    hathi_tiff_profile = imagevalidate.Profile(profile_type)
    report = hathi_tiff_profile.validate(file=test_image)
    assert len(report.issues()) == 1
    assert len(report.issues(issue_type=IssueCategory.INVALID_DATA)) == 0
    assert len(report.issues(issue_type=IssueCategory.EMPTY_DATA)) == 1
    assert len(report.issues(issue_type=IssueCategory.MISSING_FIELD)) == 0
    print(report)
    assert not report.valid


@pytest.mark.integration
@pytest.mark.parametrize("test_file,profile_name", [
    (os.path.join("empty_zip", "0000001.tif"), "HathiTrust Tiff"),
    (os.path.join("empty_zip", "0000001.jp2"), "HathiTrust JPEG 2000"),
])
def test_empty_zip(sample_data, test_file, profile_name):
    test_image = os.path.join(sample_data, test_file)
    profile_name = imagevalidate.get_profile(profile_name)
    hathi_tiff_profile = imagevalidate.Profile(profile_name)
    report = hathi_tiff_profile.validate(file=test_image)
    print(report)
    assert len(report.issues()) == 1
    assert len(report.issues(issue_type=IssueCategory.INVALID_DATA)) == 0
    assert len(report.issues(issue_type=IssueCategory.EMPTY_DATA)) == 1
    assert len(report.issues(issue_type=IssueCategory.MISSING_FIELD)) == 0
    assert not report.valid


@pytest.mark.integration
@pytest.mark.parametrize("test_file,profile_name", [
    (os.path.join("empty_phonenumber", "0000001.tif"), "HathiTrust Tiff"),
    (os.path.join("empty_phonenumber", "0000001.jp2"), "HathiTrust JPEG 2000"),
])
def test_empty_phonenumber(sample_data, test_file, profile_name):
    test_image = os.path.join(sample_data, test_file)
    profile_type = imagevalidate.get_profile(profile_name)
    hathi_tiff_profile = imagevalidate.Profile(profile_type)
    report = hathi_tiff_profile.validate(file=test_image)
    print(report)
    assert len(report.issues()) == 1
    assert len(report.issues(issue_type=IssueCategory.INVALID_DATA)) == 0
    assert len(report.issues(issue_type=IssueCategory.EMPTY_DATA)) == 1
    assert len(report.issues(issue_type=IssueCategory.MISSING_FIELD)) == 0
    assert not report.valid


@pytest.mark.integration
@pytest.mark.parametrize("test_file,profile_name", [
    (os.path.join("pixelarray", "0000001.tif"), "HathiTrust Tiff"),
    (os.path.join("pixelarray", "0000001.jp2"), "HathiTrust JPEG 2000"),
])
def test_pixelarray(sample_data, test_file, profile_name):

    test_image = os.path.join(sample_data, test_file)
    profile_name = imagevalidate.get_profile(profile_name)
    hathi_tiff_profile = imagevalidate.Profile(profile_name)
    report = hathi_tiff_profile.validate(file=test_image)
    print(report)
    assert len(report.issues()) == 1
    assert len(report.issues(issue_type=IssueCategory.INVALID_DATA)) == 1
    assert len(report.issues(issue_type=IssueCategory.EMPTY_DATA)) == 0
    assert len(report.issues(issue_type=IssueCategory.MISSING_FIELD)) == 0
    assert not report.valid
