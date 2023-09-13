import pandas as pd

from pond.artifact.pandas_dataframe_artifact import PandasDataFrameArtifact
from pond.manifest import VersionManifest
from pond.storage.file_datastore import FileDatastore
from pond.version import Version
from pond.version_name import SimpleVersionName


def test_write_then_read(tmp_path):
    data = pd.DataFrame([[1, 2]], columns=['c1', 'c2'])
    metadata = {'a': 'b'}
    version_metadata = {'source': 'test'}
    version = Version(
        version_name=SimpleVersionName(version_number=42),
        artifact=PandasDataFrameArtifact(data=data, metadata=metadata),
        manifest=VersionManifest(version_metadata),
    )
    store = FileDatastore(base_path=str(tmp_path), id='foostore')
    version.write(datastore=store, location='abc')

    assert store.exists('abc/v42')
    assert store.exists('abc/v42/_pond/manifest.yml')

    reloaded_version = Version.read(
        version_name=SimpleVersionName(version_number=42),
        artifact_class=PandasDataFrameArtifact,
        location='abc',
        datastore=store,
    )

    pd.testing.assert_frame_equal(reloaded_version.artifact.data, data)
    assert reloaded_version.artifact.metadata == {k: str(v) for k, v in metadata.items()}
