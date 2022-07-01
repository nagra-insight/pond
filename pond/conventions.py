from pond.version_name import VersionName

MANIFEST_FILENAME = 'manifest.yml'
METADATA_DIRNAME = '_pond'
LOCK_FILENAME = '_LOCK'


def manifest_location(version_location: str) -> str:
    """ Manifest location with respect to a version root. """
    return urijoinpath(version_location, METADATA_DIRNAME, MANIFEST_FILENAME)


def version_lock_file_location(version_location: str) -> str:
    return urijoinpath(version_location, METADATA_DIRNAME, LOCK_FILENAME)


def version_location(artifact_location: str, version_name: VersionName) -> str:
    return urijoinpath(artifact_location, str(version_name))


def urijoinpath(*parts) -> str:
    """Joins two uri path components, also ensure the right part does not end with a slash"""
    return '/'.join([part.rstrip('/') for part in parts])
