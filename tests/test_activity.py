from pond import Activity
from pond.artifact import Artifact
from pond.artifact.artifact_registry import ArtifactRegistry
from pond.conventions import versioned_artifact_location
from pond.metadata.metadata_source import MetadataSource
from pond.storage.file_datastore import FileDatastore
from pond.version_name import SimpleVersionName


# test: inputs are saved as metadata
# test: pond.write without giving class explicitly


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


def test_pond_write_then_read_artifact_explicit(tmp_path):
    # Can write and read artifacts when explicitly giving the artifact class
    datastore = FileDatastore(tmp_path, id='foostore')
    location = 'test_location'
    activity = Activity(
        source='test_pond.py',
        datastore=datastore,
        location=location,
        author='John Doe',
        version_name_class=SimpleVersionName,
    )

    # Save first version of the data
    data = 'test_data'
    metadata = {'test': 'xyz'}
    version = activity.write(data, name='foo', artifact_class=MockArtifact, metadata=metadata)

    first_version_name = SimpleVersionName.first()
    assert version.version_name == first_version_name
    assert version.artifact.metadata['test'] == metadata['test']
    assert datastore.exists(
        versioned_artifact_location(location, 'foo'),
    )
    assert isinstance(version.artifact, MockArtifact)

    # Write second version of the data
    data2 = 'test_data2'
    metadata2 = {'test': 'xyz2'}
    version2 = activity.write(data2, name='foo', artifact_class=MockArtifact, metadata=metadata2)
    assert version2.version_name == SimpleVersionName.next(first_version_name)

    # Read the latest version
    data_reloaded = activity.read('foo')
    assert data_reloaded == data2

    # Read the first version
    data_reloaded = activity.read('foo', version_name='v1')
    assert data_reloaded == data

    assert activity.read_history == {
        version.get_uri(location, datastore),
        version2.get_uri(location, datastore),
    }


def test_pond_write_then_read_artifact_implicit(tmp_path):
    # Can write and read artifacts, finding an appropriate artifact class
    registry = ArtifactRegistry()
    registry.register(artifact_class=MockArtifact, data_class=str)
    datastore = FileDatastore(tmp_path, id='foostore')
    activity = Activity(
        source='test_pond.py',
        datastore=datastore,
        location='test_location',
        author='John Doe',
        version_name_class=SimpleVersionName,
        artifact_registry=registry,
    )

    # Save data without artifact class
    data = 'test_data'
    metadata = {'test': 'xyz'}
    version = activity.write(data, name='foo', metadata=metadata)
    assert isinstance(version.artifact, MockArtifact)


def test_activity_metadata():
    author = 'John Doe'
    source = 'test_pond.py'
    activity = Activity(
        source=source,
        datastore=None,
        location='test_location',
        author=author,
    )
    # Mock having read some inputs
    inputs = sorted(['pond://test_location/foo/v1', 'pond://test_location/bar/v3'])
    activity.read_history = inputs

    metadata_source = activity.get_metadata()
    assert isinstance(metadata_source, MetadataSource)
    assert metadata_source.name == 'activity'
    metadata = metadata_source.collect()
    assert metadata['author'] == author
    assert metadata['inputs'] == inputs
    assert metadata['source'] == source
