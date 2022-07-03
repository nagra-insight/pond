from pond.conventions import (
    METADATA_DIRNAME,
    MANIFEST_FILENAME,
    version_manifest_location,
    urijoinpath,
)


def test_manifest_location():
    location = version_manifest_location('abc/')
    expected = f'abc/{METADATA_DIRNAME}/{MANIFEST_FILENAME}'
    assert location == expected


def test_urijoinpath():
    joined = urijoinpath('a', 'b/', 'c/')
    expected = 'a/b/c'
    assert joined == expected
