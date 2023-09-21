from typing import Any, Dict, Optional, Sequence, Set, Type, Union

from pond.artifact import Artifact
from pond.artifact.artifact_registry import global_artifact_registry
from pond.conventions import DataType, WriteMode
from pond.metadata.metadata_source import DictMetadataSource, MetadataSource
from pond.metadata.manifest import Manifest
from pond.storage.datastore import Datastore
from pond.version import Version
from pond.version_name import SimpleVersionName, VersionName
from pond.versioned_artifact import VersionedArtifact


class Activity:
    # todo: source is a Source object
    def __init__(self,
                 source: str,
                 location: str,
                 datastore: Datastore,
                 author: str,
                 version_name_class=SimpleVersionName,
                 artifact_registry=global_artifact_registry):
        self.source = source
        self.location = location
        self.datastore = datastore
        self.author = author
        self.version_name_class = version_name_class
        self.artifact_registry = artifact_registry

        #: History of all read versions, will be used as default
        #: "inputs" for written tables. Feel free to empty it whenever needed.
        self.read_history: Set[str] = set()
        #: Dict[TableRef, List[Version]]: History of all written versions
        self.write_history: Set[str] = set()

    # todo: read with metadata (read_version?)
    def read(self,
             name: str,
             version_name: Optional[Union[str, VersionName]] = None) -> Any:
        """ Read the data given its name and version name.

        See Also
        `read_version`
        """
        versioned_artifact = VersionedArtifact(
            artifact_name=name,
            location=self.location,
            datastore=self.datastore,
            artifact_class=None,  # TODO not none
            version_name_class=self.version_name_class,
        )
        version = versioned_artifact.read(version_name=version_name)
        version_id = version.get_uri(self.location, self.datastore)
        self.read_history.add(version_id)
        return version.artifact.data

    # TODO: write_artifact to write directly an artifact
    def write(self,
              data: DataType,
              name: str,
              artifact_class: Optional[Type[Artifact]] = None,
              format: Optional[str] = None,
              version_name: Optional[Union[str, VersionName]] = None,
              inputs: Optional[Sequence[str]] = None,
              metadata: Optional[Dict[str, str]] = None,
              write_mode: WriteMode = WriteMode.ERROR_IF_EXISTS) -> Version:
        # todo: write mode
        # todo: levels of metadata

        if artifact_class is None:
            artifact_class = self.artifact_registry.get_artifact(
                data_class=data.__class__,
                format=format,
            )

        versioned_artifact = VersionedArtifact(
            artifact_name=name,
            location=self.location,
            datastore=self.datastore,
            artifact_class=artifact_class,
            version_name_class=self.version_name_class,
        )

        # todo handle write mode
        # todo: handle write kwargs
        manifest = Manifest()
        if metadata is not None:
            user_metadata_source = DictMetadataSource(name='user', metadata=metadata)
            manifest.add_section(user_metadata_source)
        activity_metadata_source = self.get_metadata()
        manifest.add_section(activity_metadata_source)
        version = versioned_artifact.write(data, manifest, version_name=version_name)

        version_uri = version.get_uri(self.location, self.datastore)
        self.write_history.add(version_uri)
        return version

    def get_metadata(self) -> MetadataSource:
        """ Collect activity metadata. """
        activity_metadata = {
            'source': self.source,
            'author': self.author,
            'inputs': sorted(self.read_history),
        }
        return DictMetadataSource(name='activity', metadata=activity_metadata)

    # todo def export()
