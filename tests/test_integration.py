import os

import pytest

from uiucprescon import imagevalidate
from uiucprescon.imagevalidate import IssueCategory
import os
import tarfile
import urllib.request
from tempfile import TemporaryDirectory

# TEST_PATH = os.path.join(os.path.dirname(__file__), "henrytestmetadata")
SAMPLE_IMAGES = "https://jenkins.library.illinois.edu/userContent/metadata_test_images.tar.gz"


def download_images(url, destination):
    with TemporaryDirectory() as download_path:
        print("Downloading {}".format(url), flush=True)
        urllib.request.urlretrieve(url,
                                   filename=os.path.join(download_path,
                                                         "sample_images.tar.gz"))
        if not os.path.exists(
                os.path.join(download_path, "sample_images.tar.gz")):
            raise FileNotFoundError("sample images not download")
        print("Extracting images")
        with tarfile.open(os.path.join(download_path, "sample_images.tar.gz"),
                          "r:gz") as archive_file:
            for item in archive_file.getmembers():
                print("Extracting {}".format(item.name))
                archive_file.extract(item, path=destination)
            pass


@pytest.fixture(scope="session")
def sample_data():

    test_path = os.path.dirname(__file__)
    sample_images_path = os.path.join(test_path, "metadata_test_images")

    if os.path.exists(sample_images_path):
        print("{} already exits".format(sample_images_path))
    else:
        print("Downloading sample images")
        if not os.path.exists(sample_images_path):
            download_images(
                url=SAMPLE_IMAGES,
                destination=test_path)
    return sample_images_path


@pytest.mark.integration
@pytest.mark.parametrize("test_file,profile_name", [
    (os.path.join("bitdepth", "0000001.tif"), "HathiTiff"),
    (os.path.join("bitdepth", "0000001.jp2"), "HathiJP2000"),
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
    (os.path.join("colorspace", "0000001.tif"), "HathiTiff"),
])
def test_colorspace(sample_data, test_file, profile_name):
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
    (os.path.join("correct", "0000001.tif"), "HathiTiff"),
    (os.path.join("correct", "0000001.jp2"), "HathiJP2000"),
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
    (os.path.join("empty_address", "0000001.tif"), "HathiTiff"),
    (os.path.join("empty_address", "0000001.jp2"), "HathiJP2000"),
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
    (os.path.join("empty_city", "0000001.tif"), "HathiTiff"),
    (os.path.join("empty_city", "0000001.jp2"), "HathiJP2000"),
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
    (os.path.join("empty_country", "0000001.tif"), "HathiTiff"),
    (os.path.join("empty_country", "0000001.jp2"), "HathiJP2000"),
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
    (os.path.join("missing_creator", "0000001.tif"), "HathiTiff"),
    (os.path.join("missing_creator", "0000001.jp2"), "HathiJP2000"),
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
    (os.path.join("empty_state", "0000001.tif"), "HathiTiff"),
    (os.path.join("empty_state", "0000001.jp2"), "HathiJP2000"),
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
    (os.path.join("empty_zip", "0000001.tif"), "HathiTiff"),
    (os.path.join("empty_zip", "0000001.jp2"), "HathiJP2000"),
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
    (os.path.join("empty_phonenumber", "0000001.tif"), "HathiTiff"),
    (os.path.join("empty_phonenumber", "0000001.jp2"), "HathiJP2000"),
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
    (os.path.join("pixelarray", "0000001.tif"), "HathiTiff"),
    (os.path.join("pixelarray", "0000001.jp2"), "HathiJP2000"),
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
