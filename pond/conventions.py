MANIFEST_FILENAME = 'manifest.yml'
METADATA_DIRNAME = '_pond'
TXT_ENCODING = 'utf-8'


def manifest_location(version_location: str) -> str:
    """ Manifest location with respect to a version root. """
    return urijoinpath(version_location, METADATA_DIRNAME, MANIFEST_FILENAME)


def urijoinpath(*parts) -> str:
    """Joins two uri path components, also ensure the right part does not end with a slash"""
    return '/'.join([part.rstrip('/') for part in parts])
