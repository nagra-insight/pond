from pond.conventions import (
    METADATA_DIRNAME,
    MANIFEST_FILENAME,
    version_data_location, version_manifest_location,
    urijoinpath,
)


def test_urijoinpath():
    joined = urijoinpath('a', 'b/', 'c/')
    expected = 'a/b/c'
    assert joined == expected


def test_data_location():
    location = version_data_location('abc/', 'blah.bin')
    expected = f'abc/blah.bin'
    assert location == expected


def test_manifest_location():
    location = version_manifest_location('abc/')
    expected = f'abc/{METADATA_DIRNAME}/{MANIFEST_FILENAME}'
    assert location == expected
