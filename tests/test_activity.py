from pond.activity import Activity
from pond.artifact import Artifact
from pond.conventions import version_location, versioned_artifact_location
from pond.storage.file_datastore import FileDatastore
from pond.version_name import SimpleVersionName


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


def test_activity_write_then_read_artifact_explicit(tmp_path):
    # Can write and read artifacts when explicitly giving the artifact class
    datastore = FileDatastore(tmp_path)
    activity = Activity(
        source='test_activity.py',
        datastore=datastore,
        location='test_location',
        author='John Doe',
    )

    # Save first version of the data
    data = 'test_data'
    metadata = {'test': 'xyz'}
    version = activity.write(data, name='foo', artifact_class=MockArtifact, metadata=metadata)

    first_version_name = SimpleVersionName.first()
    assert version.version_name == first_version_name
    assert version.artifact.metadata == metadata
    assert datastore.exists(
        versioned_artifact_location('test_location', 'foo'),
    )
    assert isinstance(version.artifact, MockArtifact)

    # Write second version of the data
    data2 = 'test_data'
    metadata2 = {'test': 'xyz'}
    version2 = activity.write(data2, name='foo', artifact_class=MockArtifact, metadata=metadata2)

    # Read the latest version
    data_reloaded = activity.read('foo')
    assert data_reloaded == data2

    # Read the first version
    data_reloaded = activity.read('foo', version_name='v1')
    assert data_reloaded == data
