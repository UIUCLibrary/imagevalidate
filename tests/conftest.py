import os
import shutil
import tarfile
import urllib.request
from tempfile import TemporaryDirectory

import pytest

SAMPLE_IMAGES = "https://jenkins.library.illinois.edu/userContent/metadata_test_images.tar.gz"


def pytest_addoption(parser):
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="run integration tests"
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--integration"):
        # --integration given in cli: do not skip integration tests
        return

    skip_integration = pytest.mark.skip(
        reason="skipped integration tests. Use --integration option to run")

    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)

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
    yield sample_images_path
    shutil.rmtree(sample_images_path)
