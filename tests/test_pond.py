import os
import pytest

from pond import Pond
from pond.artifact import Artifact
from pond.artifact.pandas_dataframe_artifact import PandasDataFrameArtifact
from pond.conventions import version_location
from pond.exceptions import ArtifactVersionDoesNotExist
from pond.manifest import VersionManifest
from pond.storage.file_datastore import FileDatastore
from pond.version_name import SimpleVersionName
from pond.versioned_artifact import VersionedArtifact


class MockArtifact(Artifact):
    @classmethod
    def _read_bytes(cls, file_, **kwargs):
        data = file_.read().decode()
        return cls(data=data)

    def write_bytes(self, file_, **kwargs):
        file_.write(str.encode(self.data))

    @staticmethod
    def filename(basename):
        return basename + '.mock'


# activity.write(artifact, artifact_name)
# - use artifact_name to look for a versioned artifact in a given datastore and location
#   - if it doesn't exist, create it; use the artifact.class to create a versioned artifact of
#   that kind
#   - if it does exist, check that the artifact class corresponds to the versioned artifact
#   metadata

def test_pond_write_then_read(tmp_path):
    datastore = FileDatastore(tmp_path)
    pond = Pond(
        source='test_source',
        author='test_author',
        datastore=datastore,
        location='loc',
        version_name_class=SimpleVersionName,
    )

    # create first version
    data = 'abc'
    metadata = {'test': 'xyz'}
    version = pond.write(data=data, name='test_data', metadata=metadata, artifact_class=MockArtifact)

    first_version_name = SimpleVersionName.first()
    assert version.version_name == first_version_name
    assert version.artifact.data == data
    assert version.artifact.metadata['test'] == 'xyz'
    # todo: this shouldn't be here
    assert version.metadata['artifact_class'] == 'MockArtifact'
    #assert version.metadata['version_name_class'] == 'SimpleVersionName'
    assert datastore.exists('loc/test_data/v1')

    # Reload the first version
    reloaded_data = pond.read(name='test_data', version_name=first_version_name)
    assert reloaded_data == data

    # todo: separate test
    # Reload the latest version
    reloaded_data = pond.read(name='test_data')
    assert reloaded_data == data


# test: inputs are saved as metadata
# test: pond.write without giving class explicitly
