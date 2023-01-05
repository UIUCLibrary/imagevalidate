from unittest.mock import MagicMock, Mock

import pytest

from uiucprescon.imagevalidate import common
import py3exiv2bind


class TestColorSpaceIccPrefCcmCheck:

    def test_no_pref_ccm_raises(self, monkeypatch):
        tester = common.ColorSpaceIccPrefCcmCheck()
        monkeypatch.setattr(
            py3exiv2bind,
            "Image",
            Mock(return_value=Mock(icc=Mock(return_value={})))
        )
        with pytest.raises(common.InvalidStrategy) as e:
            tester.check("dummy.tif")
            assert "No pref_ccm key found" in str(e)

    def test_valid_pref_ccm(self, monkeypatch):
        tester = common.ColorSpaceIccPrefCcmCheck()
        monkeypatch.setattr(
            py3exiv2bind,
            "Image",
            Mock(
                return_value=Mock(
                    icc=Mock(return_value={'pref_ccm': Mock(value=b'spam')})
                )
            )
        )
        tester.check("dummy.tif")


class TestColorSpaceIccDeviceModelCheck:
    def test_no_device_model_raises(self, monkeypatch):
        tester = common.ColorSpaceIccDeviceModelCheck()

        monkeypatch.setattr(
            py3exiv2bind,
            "Image",
            Mock(return_value=Mock(icc=Mock(return_value={})))
        )
        with pytest.raises(common.InvalidStrategy) as e:
            tester.check("dummy.tif")
            assert "No device_model key found" in str(e)
