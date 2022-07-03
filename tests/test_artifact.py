import pytest
import datetime
import os

from pond.conventions import version_location
from pond.exceptions import ArtifactVersionDoesNotExist
from pond.artifact import Artifact, FIRST_VERSION_NAME
from pond.manifest import VersionManifest
from pond.storage.file_datastore import FileDatastore
from pond.version_name import SimpleVersionName


def test_version_names():
    artifact = Artifact(FileDatastore(os.getcwd()), 'fixtures/table_csv')

    assert artifact.all_version_names() == [SimpleVersionName(1), SimpleVersionName(2)]
    assert artifact.version_names() == [SimpleVersionName(1)]
    assert artifact.latest_version_name() == SimpleVersionName(1)
    assert artifact.latest_version().location == 'fixtures/table_csv/v1'
    assert artifact.version().location == 'fixtures/table_csv/v1'

    with pytest.raises(ArtifactVersionDoesNotExist):
        artifact.version('v2')


def test_create_delete_versions(tmp_path):
    artifact = Artifact(FileDatastore(os.getcwd()), str(tmp_path))

    # create initial version
    version = artifact.create_version()
    assert version is not None
    assert version.name == FIRST_VERSION_NAME
    assert os.path.exists(version.location)

    # create another version
    version = artifact.create_version()
    assert version is not None
    assert version.name == FIRST_VERSION_NAME.next()
    assert os.path.exists(version.location)

    # check version name list
    assert artifact.all_version_names() == [FIRST_VERSION_NAME, FIRST_VERSION_NAME.next()]
    assert artifact.version_names() == []

    # make last one existing
    version.write_manifest(VersionManifest(id='id'))
    assert os.path.exists(version.manifest_location)
    assert version.exists()
    assert artifact.version_names() == [version.name]

    # delete FIRST_VERSION_NAME
    artifact.delete_version(FIRST_VERSION_NAME)
    assert not os.path.exists(version_location(artifact.location, FIRST_VERSION_NAME))
    assert artifact.all_version_names() == [version.name]
    assert artifact.version_names() == [version.name]
