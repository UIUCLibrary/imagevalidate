from uiucprescon.imagevalidate import openjp2wrap
import pytest

def test_dummy():
    print(openjp2wrap.open_jpeg_version())

def test_get_colorspace_exists():
    assert hasattr(openjp2wrap, "get_bit_depth")

def test_invalid_get_bitdeph_throws_exception():
    source = "fakefile.jp2"
    with pytest.raises(openjp2wrap.InvalidFileException) as excinfo:
        openjp2wrap.get_bit_depth(source)
    assert source in str(excinfo.value)
