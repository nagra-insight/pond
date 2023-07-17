from typing import Dict, Optional, Sequence, Type, Union

from pond.artifact import Artifact
from pond.conventions import DataType, SaveMode
from pond.storage.datastore import Datastore
from pond.version import Version
from pond.version_name import SimpleVersionName, VersionName
from pond.versioned_artifact import VersionedArtifact


class Activity:
    def __init__(self,
                 source: str,
                 location: str,
                 datastore: Datastore,
                 author: str,
                 version_name_class=SimpleVersionName):
        self.source = source
        self.location = location
        self.datastore = datastore
        self.author = author
        self.version_name_class = version_name_class

    def read(self,
             name: str,
             version_name: Optional[Union[str, VersionName]] = None) -> DataType:
        versioned_artifact = VersionedArtifact(
            artifact_name=name,
            location=self.location,
            datastore=self.datastore,
        )
        version = versioned_artifact.read(version_name=version_name)
        return version

    def write(self,
              data: DataType,
              name: str,
              artifact_class: Type[Artifact],
              version_name: Optional[Union[str, VersionName]] = None,
              inputs: Optional[Sequence[str]] = None,
              metadata: Optional[Dict[str, str]] = None,
              save_mode: SaveMode = SaveMode.ERROR_IF_EXISTS) -> Version:
        versioned_artifact = VersionedArtifact(
            artifact_name=name,
            location=self.location,
            datastore=self.datastore,
            artifact_class=artifact_class,
            version_name_class=self.version_name_class,
        )
        version = versioned_artifact.write(data, metadata, version_name=version_name)
        return version

    # def export()
