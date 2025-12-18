import hashlib
import shutil

import pytest

from uiucprescon import imagevalidate
from uiucprescon.imagevalidate import IssueCategory
import os
import tarfile
import urllib.request
from tempfile import TemporaryDirectory

# TEST_PATH = os.path.join(os.path.dirname(__file__), "henrytestmetadata")
SAMPLE_IMAGES = "https://nexus.library.illinois.edu/repository/sample-data/images/metadata_test_images.tar.gz"
SAMPLE_IMAGES_SHA256 = "eee5fa3641628c7365e14de3f58da069cb332dc13a4b739dc168a1617109ebbf"

# To save time from redownloading the metadata_test_images.tar.gz file every time,
# download it locally and set the environment variable SAMPLE_IMAGES_ARCHIVE
# to the path of the downloaded file

def download_images(url, download_path):

    print(f"Downloading {url}")
    output = os.path.join(download_path, "sample_images.tar.gz")
    urllib.request.urlretrieve(url, filename=output)
    if not os.path.exists(output):
        raise FileNotFoundError("sample images not download")
    return output

@pytest.fixture(scope="session")
def sample_data():

    test_path = os.path.dirname(__file__)
    sample_images_path = os.path.join(test_path, "metadata_test_images")

    if os.path.exists(sample_images_path):
        print("{} already exits".format(sample_images_path))
    else:
        archive = os.getenv('SAMPLE_IMAGES_ARCHIVE')
        if not archive:
            print("Downloading sample images")
            if not os.path.exists(sample_images_path):
                archive = download_images(
                    url=SAMPLE_IMAGES,
                    download_path=test_path
                )
        if not os.path.exists(archive):
            raise FileNotFoundError(f"sample image archive not found. {archive} does not exist.")
        verify_hash(archive, sha256_hash=SAMPLE_IMAGES_SHA256)
        extract_images(path=archive, destination=test_path)
    yield sample_images_path
    shutil.rmtree(sample_images_path)

def extract_images(path, destination):
    print("Extracting images")
    with tarfile.open(path, "r:gz") as archive_file:
        for item in archive_file.getmembers():
            print("Extracting {}".format(item.name))
            archive_file.extract(item, path=destination)

def verify_hash(path, sha256_hash):
    with open(path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    assert file_hash == sha256_hash


@pytest.mark.integration
@pytest.mark.parametrize("test_file,profile_name", [
    (os.path.join("bitdepth", "0000001.tif"), "HathiTrust Tiff"),
    (os.path.join("bitdepth", "0000001.jp2"), "HathiTrust JPEG 2000"),
])
@pytest.mark.filterwarnings('ignore:.*Reading non-standard UUID-EXIF_bad box in*:Warning')
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
@pytest.mark.filterwarnings('ignore:.*Reading non-standard UUID-EXIF_bad box in*:Warning')
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
@pytest.mark.filterwarnings('ignore:.*Reading non-standard UUID-EXIF_bad box in*:Warning')
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
@pytest.mark.filterwarnings('ignore:.*Reading non-standard UUID-EXIF_bad box in*:Warning')
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
@pytest.mark.filterwarnings('ignore:.*Reading non-standard UUID-EXIF_bad box in*:Warning')
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
@pytest.mark.filterwarnings('ignore:.*Reading non-standard UUID-EXIF_bad box in*:Warning')
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
@pytest.mark.filterwarnings('ignore:.*Reading non-standard UUID-EXIF_bad box in*:Warning')
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
@pytest.mark.filterwarnings('ignore:.*Reading non-standard UUID-EXIF_bad box in*:Warning')
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
@pytest.mark.filterwarnings('ignore:.*Reading non-standard UUID-EXIF_bad box in*:Warning')
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
@pytest.mark.filterwarnings('ignore:.*Reading non-standard UUID-EXIF_bad box in*:Warning')
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
@pytest.mark.filterwarnings('ignore:.*Reading non-standard UUID-EXIF_bad box in*:Warning')
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
@pytest.mark.filterwarnings('ignore:.*Reading non-standard UUID-EXIF_bad box in*:Warning')
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
