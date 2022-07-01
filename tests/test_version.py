import os

from pond.conventions import manifest_location
from pond.storage.file_datastore import FileDatastore
from pond.version import Version
from pond.version_name import SimpleVersionName


def test_exists(tmp_path):
    version_name = SimpleVersionName(version_number=13)
    store = FileDatastore(base_path=tmp_path)

    # False if manifest does not exists
    version_location = str(tmp_path / str(version_name))
    version = Version(name=version_name, location=version_location, store=store)
    assert not version.exists()

    # True if manifest has been loaded
    version = Version(name=version_name, location=version_location, store=store)
    version._manifest = 'mock'
    assert version.exists()

    # True if manifest file exists
    manifest_path = manifest_location(version_location)
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    store.write(manifest_path, b'abc')
    version = Version(name=version_name, location=version_location, store=store)
    assert version.exists()
