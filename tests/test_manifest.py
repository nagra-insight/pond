from pond.manifest import ArtifactManifest
from pond.storage.file_datastore import FileDatastore


def test_artifact_manifest_to_dict(tmp_path):
    manifest = ArtifactManifest({'foo': 'bar'})
    assert manifest.to_dict() == {'metadata': {'foo': 'bar'}}


def test_artifact_manifest_write_yaml(tmp_path):
    manifest = ArtifactManifest({'foo': 'bar'})
    datastore = FileDatastore(tmp_path)
    manifest.write_yaml(location='test.yml', datastore=datastore)
    assert datastore.exists(tmp_path / 'test.yml')
    assert datastore.read_yaml('test.yml') == {'metadata': {'foo': 'bar'}}
