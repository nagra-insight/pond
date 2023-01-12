from pond.version_name import VersionName


MANIFEST_FILENAME = 'manifest.yml'
METADATA_DIRNAME = '_pond'
TXT_ENCODING = 'utf-8'
VERSIONS_LOCK_FILENAME = '_VERSIONS_LOCK'


def urijoinpath(*parts: str) -> str:
    """Joins two uri path components, also ensure the right part does not end with a slash"""
    return '/'.join([part.rstrip('/') for part in parts])


def version_location(location: str, version_name: VersionName) -> str:
    return urijoinpath(location, str(version_name))


def versions_lock_file_location(location: str) -> str:
    return urijoinpath(location, METADATA_DIRNAME, VERSIONS_LOCK_FILENAME)


def version_data_location(version_location: str, data_filename: str) -> str:
    return urijoinpath(version_location, data_filename)


def version_manifest_location(version_location: str) -> str:
    """ Manifest location with respect to a version root. """
    return urijoinpath(version_location, METADATA_DIRNAME, MANIFEST_FILENAME)
