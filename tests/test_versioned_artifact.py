import os
import pytest

from pond.artifact import Artifact
from pond.artifact.pandas_dataframe_artifact import PandasDataFrameArtifact
from pond.conventions import version_location
from pond.exceptions import ArtifactVersionDoesNotExist
from pond.manifest import VersionManifest
from pond.storage.file_datastore import FileDatastore
from pond.version_name import SimpleVersionName
from pond.versioned_artifact import VersionedArtifact


# def test_version():
#     datastore = FileDatastore(os.getcwd())
#     versioned_artifact = VersionedArtifact(
#         artifact_name='table_csv',
#         location=os.path.join(datastore.base_path, 'fixtures'),
#         datastore=datastore,
#         artifact_class=PandasDataFrameArtifact,
#         version_name_class=SimpleVersionName,
#     )
#     version = versioned_artifact.version('v1')
#     assert version is not None
#     assert version.name == SimpleVersionName(1)
#     assert version.location == 'fixtures/table_csv/v1'
#     assert version.manifest_location == 'fixtures/table_csv/v1/manifest.yaml'
#     assert version.data_location == 'fixtures/table_csv/v1/data.csv'
#     assert version.exists()
#     assert version.manifest.id == 'table_csv'
#     assert version.manifest.data_filename == 'data.csv'
#     assert version.manifest.artifact == {'name': 'table_csv', 'type': 'csv'}
#
#     # delete version
#     versioned_artifact.delete_version('v1')
#     assert not os.path.exists(version.location)
#     assert not version.exists()




# def test_version_names():
#     datastore = FileDatastore(os.getcwd())
#     versioned_artifact = VersionedArtifact(
#         artifact_name='table_csv',
#         location=os.path.join(datastore.base_path, 'fixtures'),
#         datastore=datastore,
#         version_name_class=SimpleVersionName,
#     )
#     print(versioned_artifact.versions_location)
#
#     assert versioned_artifact.all_version_names() == [SimpleVersionName(1), SimpleVersionName(2)]
#     assert versioned_artifact.version_names() == [SimpleVersionName(1)]
#     assert versioned_artifact.latest_version_name() == SimpleVersionName(1)
#     assert versioned_artifact.latest_version().location == 'fixtures/table_csv/v1'
#     assert versioned_artifact.version().location == 'fixtures/table_csv/v1'
#
#     with pytest.raises(ArtifactVersionDoesNotExist):
#         versioned_artifact.version('v2')


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

def test_versioned_artifact_write_then_read(tmp_path):
    datastore = FileDatastore(tmp_path)
    versioned_artifact = VersionedArtifact(
        artifact_name='test_artifact',
        location='test_location',
        datastore=datastore,
        artifact_class=MockArtifact,
        version_name_class=SimpleVersionName,
    )

    assert datastore.exists(versioned_artifact.versions_location)
    assert datastore.exists(versioned_artifact.versions_list_location)
    assert versioned_artifact.version_names() == []

    # create first version
    data = 'test_data'
    metadata = {'test': 'xyz'}
    version = versioned_artifact.write(data=data, metadata=metadata)

    first_version_name = SimpleVersionName.first()
    assert version.version_name == first_version_name

    # Reload the first version
    reloaded_artifact = versioned_artifact.read(version_name=first_version_name)
    assert isinstance(reloaded_artifact.artifact, MockArtifact)
    assert reloaded_artifact.artifact.data == data
    assert reloaded_artifact.artifact.metadata == metadata

    # create another version
    version2 = versioned_artifact.write(data='data2', metadata={})
    assert version2.version_name == SimpleVersionName.next(version.version_name)

    # check version name list
    assert versioned_artifact.version_names() == [first_version_name, version2.version_name]


# test: all_version_names vs version_names
# test: delete version
