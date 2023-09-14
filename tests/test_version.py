from datetime import datetime
import pandas as pd

from pond.artifact.pandas_dataframe_artifact import PandasDataFrameArtifact
from pond.manifest import VersionManifest
from pond.metadata.metadata_source import MetadataSource
from pond.storage.file_datastore import FileDatastore
import pond.version
from pond.version import Version
from pond.version_name import SimpleVersionName


def test_write_then_read(tmp_path):
    data = pd.DataFrame([[1, 2]], columns=['c1', 'c2'])
    metadata = {'a': 'b'}
    version_metadata = {'source': 'test'}
    artifact_name = 'meh'
    version = Version(
        artifact_name=artifact_name,
        version_name=SimpleVersionName(version_number=42),
        artifact=PandasDataFrameArtifact(data=data, metadata=metadata),
        manifest=VersionManifest(version_metadata),
    )
    store = FileDatastore(base_path=str(tmp_path), id='foostore')
    version.write(location='abc', datastore=store, metadata_sources=[])

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
    assert reloaded_version.artifact_name == artifact_name


def test_version_uri(tmp_path):
    data = pd.DataFrame([[1, 2]], columns=['c1', 'c2'])
    version_name = SimpleVersionName(version_number=42)
    version = Version(
        artifact_name='foo',
        version_name=version_name,
        artifact=PandasDataFrameArtifact(data=data),
        manifest=None,
    )
    store = FileDatastore(base_path=str(tmp_path), id='foostore')
    uri = version.get_uri(location='exp1', datastore=store)
    assert uri == 'pond://foostore/exp1/foo/v42'


def mock_datetime_now(module, date_time_now, monkeypatch):
    class MockDatetime(datetime):
        @classmethod
        def now(cls):
            return date_time_now

    monkeypatch.setattr(module, "datetime", MockDatetime)


def test_version_metadata(tmp_path, monkeypatch):
    data = pd.DataFrame([[1, 2]], columns=['c1', 'c2'])
    version_name = SimpleVersionName(version_number=42)
    version = Version(
        artifact_name='foo',
        version_name=version_name,
        artifact=PandasDataFrameArtifact(data=data),
        manifest=None,
    )

    date_time_now = datetime(2020, 12, 25, 17, 5, 55)
    mock_datetime_now(pond.version.datetime, date_time_now, monkeypatch)

    store = FileDatastore(base_path=str(tmp_path), id='foostore')
    data_filename = 'foo.csv'

    metadata_source = version.get_metadata('exp1', store, data_filename)

    assert isinstance(metadata_source, MetadataSource)
    assert metadata_source.name == 'version'
    metadata = metadata_source.collect()
    assert metadata['filename'] == data_filename
    assert metadata['uri'] == 'pond://foostore/exp1/foo/v42'
    assert metadata['date_time'] == date_time_now
