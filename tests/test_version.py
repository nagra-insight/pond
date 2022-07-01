import os

from pond.conventions import manifest_location
from pond.manifest import VersionManifest
from pond.storage.file_datastore import FileDatastore
from pond.version import Version
from pond.version_name import SimpleVersionName


def test_exists(tmp_path):
    store = FileDatastore(base_path=tmp_path)
    version_name = SimpleVersionName(version_number=13)

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
    store.create_dir(os.path.dirname(manifest_path))
    store.write(manifest_path, b'abc')
    version = Version(name=version_name, location=version_location, store=store)
    assert version.exists()


def test_manifest(tmp_path):
    store = FileDatastore(base_path=tmp_path)

    version_name = SimpleVersionName(version_number=13)
    version_location = str(tmp_path / str(version_name))
    manifest_path = manifest_location(version_location)
    content = {'version': version_name.version_number, 'value': 123}
    store.create_dir(os.path.dirname(manifest_path))
    store.write_yaml(manifest_path, content)

    version = Version(name=version_name, location=version_location, store=store)
    manifest = version.manifest()
    assert isinstance(manifest, VersionManifest)
    assert manifest.to_dict() == content


def test_write_manifest(tmp_path):
    store = FileDatastore(base_path=tmp_path)
    version_name = SimpleVersionName(version_number=13)
    version_location = str(tmp_path / str(version_name))
    version = Version(name=version_name, location=version_location, store=store)

    content = {'version': version_name.version_number, 'value': 123}
    manifest = VersionManifest.from_dict(content)

    assert not version.exists()
    version.write_manifest(manifest)
    assert version.exists()


def test_write_manifest_not_exist_if_fail(tmp_path):
    store = FileDatastore(base_path=tmp_path)
    version_name = SimpleVersionName(version_number=13)
    version_location = str(tmp_path / str(version_name))
    version = Version(name=version_name, location=version_location, store=store)

    assert not version.exists()

    try:
        # The write operation is expected to fail
        manifest = 'does not serialize'
        version.write_manifest(manifest)
    except AttributeError:
        pass

    # The manifest should not exist, since it has not been written
    assert not version.exists()
