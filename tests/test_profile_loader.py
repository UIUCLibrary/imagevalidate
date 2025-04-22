from uiucprescon import imagevalidate


def test_get_all_profiles():
    profiles = imagevalidate.available_profiles()
    assert isinstance(profiles, set)

def test_get_all_profiles_is_not_empty():
    profiles = imagevalidate.available_profiles()
    assert len(profiles) > 0


#
def test_get_hathi_tiff_profile():
    hathi_tiff_profile = imagevalidate.get_profile("HathiTrust JPEG 2000")
    assert isinstance(hathi_tiff_profile, imagevalidate.profiles.AbsProfile)
