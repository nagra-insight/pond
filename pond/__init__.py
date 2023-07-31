from typing import Any, Dict, Optional, Type, Union

from pond.artifact import Artifact
from pond.entities import WriteMode
from pond.storage.datastore import Datastore
from pond.version import Version
from pond.version_name import SimpleVersionName, VersionName
from pond.versioned_artifact import VersionedArtifact


class Pond:
    # todo: source is a Source object
    def __init__(self, source: str, author: str, datastore: Datastore,
                 location='str', version_name_class: Type[VersionName]=SimpleVersionName):
        self.source = source
        self.author = author
        self.datastore = datastore
        self.location = location
        self.version_name_class = version_name_class

    # todo: read with metadata (read_version?)
    def read(self,
             name: str,
             version_name: Optional[Union[str, VersionName]] = None) -> Any:

        versioned_artifact = VersionedArtifact(
            artifact_name=name,
            location=self.location,
            datastore=self.datastore,
            artifact_class=None,
            version_name_class=None,
        )
        version = versioned_artifact.read(version_name)
        return version.artifact.data

    def write(self,
              data: Any,
              name: str,
              metadata: Optional[Dict[str, str]] = None,
              artifact_class: Optional[Type[Artifact]] = None,
              version_name: Optional[Union[str, VersionName]] = None,
              save_mode: WriteMode = WriteMode.ERROR_IF_EXISTS) -> Version:
        # todo: levels of metadata
        metadata = metadata or {}
        metadata['source'] = self.source
        metadata['author'] = self.author
        #if not inputs:
        #    inputs = self.get_read_ids()
        #inputs = [conventions.validate_uri(uri) for uri in inputs]

        # todo: artifact_name -> name
        # todo: switch position of location and datastore
        versioned_artifact = VersionedArtifact(
            artifact_name=name,
            location=self.location,
            datastore=self.datastore,
            artifact_class=artifact_class,
            version_name_class=self.version_name_class,
        )
        # todo handle save mode
        # todo: handle write kwargs
        version = versioned_artifact.write(data, metadata, version_name)

        return version
