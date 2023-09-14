import datetime

from pond.artifact import Artifact
from pond.conventions import (
    version_data_location,
    version_location,
    version_manifest_location,
    version_uri,
)
from pond.manifest import VersionManifest
from pond.metadata.metadata_source import DictMetadataSource
from pond.storage.datastore import Datastore
from pond.version_name import VersionName


class Version:
    # TODO: Version does not load the artifact, it only loads the manifest.

    def __init__(self, artifact_name: str, version_name: VersionName, artifact: Artifact,
                 manifest: VersionManifest):
        """ Manages a version: its manifest, data, and data store locations.

        Parameters
        ----------
        artifact
        manifest
        version_name VersionName
            Name of the version
        location: str
            URI where the version is written
        datastore: : DataStore
            DataStore instance
        """
        self.artifact_name = artifact_name
        self.version_name = version_name
        self.manifest = manifest
        self.artifact = artifact
        self.metadata = {'artifact_class': type(artifact).__name__}


    def get_metadata(self, location, datastore, data_filename):
        version_metadata = {
            'uri': self.get_uri(location, datastore),
            'filename': data_filename,
            'date_time': datetime.datetime.now()
        }
        version_metadata_source = DictMetadataSource(name='version', metadata=version_metadata)
        return version_metadata_source


    def write(self, location: str, datastore: Datastore, metadata_sources, **artifact_write_kwargs):
        manifest = self.manifest.to_dict()

        #: location of the version folder
        version_location_ = version_location(location, self.version_name)
        #: location of the manifest file
        manifest_location = version_manifest_location(version_location_)
        #: filename for the saved data
        data_filename = manifest.get('data_filename', None)
        if data_filename is None:
            data_basename = '{self.artifact.name}_{str(self.version_name)}'
            data_filename = self.artifact.filename(data_basename)
            manifest['data_filename'] = data_filename

        #artifact_metadata_source = self.artifact.get_metadata(location, datastore, data_filename)

        # TODO do I need to do this, or save multiple files?
        manifest['artifact'] = self.artifact.metadata
        # TODO change this
        manifest['artifact_name'] = self.artifact_name
        # TODO need real URI
        manifest['uri'] = f'pond://{location}/artifact_name?/{str(self.version_name)}'

        # TODO this should be responsibility of the manifest
        datastore.write_yaml(manifest_location, manifest)

        datastore.makedirs(version_location_)
        data_location = version_data_location(version_location_, data_filename)
        with datastore.open(data_location, 'wb') as f:
            self.artifact.write_bytes(f, **artifact_write_kwargs)
        # TODO return storage manifest?


    # todo adjust location, datastore order here and in write
    @classmethod
    def read(cls, version_name, artifact_class, location, datastore):
        #: location of the version folder
        version_location_ = version_location(location, version_name)
        #: location of the manifest file
        manifest_location = version_manifest_location(version_location_)

        # TODO this should be the responsibility of the manifest
        manifest_yaml = datastore.read_yaml(manifest_location)
        manifest = VersionManifest(manifest_yaml).to_dict()

        data_filename = manifest['data_filename']
        artifact_metadata = manifest['artifact']
        data_location = version_data_location(version_location_, data_filename)
        with datastore.open(data_location, 'rb') as f:
            artifact = artifact_class.read_bytes(f, metadata=artifact_metadata)

        version = cls(
            artifact_name=manifest['artifact_name'],
            version_name=version_name,
            artifact=artifact,
            manifest=manifest,
        )
        return version

    def get_uri(self, location, datastore):
        """ Build URI for a specific location and datastore. """
        uri = version_uri(datastore.id, location, self.artifact_name, self.version_name)
        return uri
