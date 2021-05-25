from uiucprescon.imagevalidate import openjp2wrap


def test_dummy():
    print(openjp2wrap.open_jpeg_version())

def test_get_colorspace_exists():
    assert hasattr(openjp2wrap, "get_bitdeph")

