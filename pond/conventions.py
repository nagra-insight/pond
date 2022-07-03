from pond.version_name import VersionName

VERSIONS_LOCK_FILENAME = '_VERSIONS_LOCK'
MANIFEST_FILENAME = 'manifest.yml'
METADATA_DIRNAME = '_pond'
TXT_ENCODING = 'utf-8'


def version_manifest_location(version_location: str) -> str:
    """ Manifest location with respect to a version root. """
    return urijoinpath(version_location, METADATA_DIRNAME, MANIFEST_FILENAME)


def urijoinpath(*parts: str) -> str:
    """Joins two uri path components, also ensure the right part does not end with a slash"""
    return '/'.join([part.rstrip('/') for part in parts])


def versions_lock_file_location(artifact_location: str) -> str:
    return urijoinpath(artifact_location, METADATA_DIRNAME, VERSIONS_LOCK_FILENAME)


def version_location(artifact_location: str, version_name: VersionName) -> str:
    return urijoinpath(artifact_location, str(version_name))
