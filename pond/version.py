from uuid import uuid4

from pond.artifact import Artifact
from pond.conventions import (
    version_data_location, version_location,
    version_manifest_location,
)
from pond.manifest import VersionManifest
from pond.storage.datastore import Datastore
from pond.version_name import VersionName


class Version:

    def __init__(self, version_name: VersionName, artifact: Artifact, manifest: VersionManifest):
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
        self.version_name = version_name
        self.manifest = manifest
        self.artifact = artifact

    def write(self, datastore: Datastore, location: str, **artifact_write_kwargs):
        manifest = self.manifest.to_dict()

        #: location of the version folder
        version_location_ = version_location(location, self.version_name)
        #: location of the manifest file
        manifest_location = version_manifest_location(version_location_)
        #: filename for the saved data
        data_filename = manifest.get('data_filename', None)
        if data_filename is None:
            data_filename = self.artifact.filename(str(uuid4()))
            manifest['data_filename'] = data_filename

        # TODO do I need to do this, or save multiple files?
        manifest['artifact'] = self.artifact.metadata
        # TODO this should be responsibility of the manifest
        datastore.write_yaml(manifest_location, manifest)

        datastore.makedirs(version_location_)
        data_location = version_data_location(version_location_, data_filename)
        with datastore.open(data_location, 'wb') as f:
            self.artifact.write_bytes(f, **artifact_write_kwargs)
        # TODO return storage manifest?

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

        return cls(version_name=version_name, artifact=artifact, manifest=manifest)
