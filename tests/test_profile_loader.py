from uiucprescon import imagevalidate


def test_get_all_profiles():
    profiles = imagevalidate.available_profiles()
    assert isinstance(profiles, set)


#
def test_get_hathi_tiff_profile():
    hathi_tiff_profile = imagevalidate.get_profile("HathiTiff")
    assert isinstance(hathi_tiff_profile, imagevalidate.profiles.AbsProfile)
