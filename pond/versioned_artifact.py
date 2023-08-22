import json
import logging
import time
from typing import List, Optional, Type, Union

from pond.artifact import Artifact
from pond.conventions import WriteMode, version_manifest_location, version_location, \
    versions_lock_file_location, versioned_artifact_location
from pond.exceptions import ArtifactHasNoVersion, ArtifactVersionAlreadyExists, ArtifactVersionsIsLocked
from pond.manifest import VersionManifest
from pond.storage.datastore import Datastore
from pond.version import Version
from pond.version_name import VersionName

logger = logging.getLogger(__name__)

# Time to wait before retrying when creating a new version fails
NEW_VERSION_WAIT_MS = 1000


class VersionedArtifact:

    def __init__(self, name: str, location: str, datastore: Datastore,
                 artifact_class: Type[Artifact], version_name_class: Type[VersionName]):
        """

        Parameters
        ----------
        datastore
        location
        """
        self.name = name
        self.location = location
        self.datastore = datastore
        self.artifact_class = artifact_class
        self.version_name_class = version_name_class
        self.manifest = {}

        self.versions_location = versioned_artifact_location(location, name)
        # todo this goes to conventions.py
        self.versions_list_location = f'{self.versions_location}/versions.json'
        self.manifest_location = f'{self.versions_location}/manifest.yml'

        if not self.datastore.exists(self.versions_location):
            # Create the versioned artifact folder organization
            self.datastore.makedirs(self.versions_location)
            self._write_version_names([])
            self.manifest['artifact_class'] = artifact_class.class_id()
            self.manifest['version_name_class'] = version_name_class.class_id()
            self._write_manifest()

        else:
            # Load the versioned artifact metadata, including the artifact class and the version
            # names class. If they are different from the ones passed in the constructor,
            # raise an exception.
            self.metadata = self._read_manifest()
            artifact_class_id = self.metadata['artifact_class']
            self.artifact_class = Artifact.subclass_from_id(artifact_class_id)
            version_name_class_id = self.metadata['version_name_class']
            self.version_name_class = VersionName.subclass_from_id(version_name_class_id)

    def _write_manifest(self):
        self.datastore.write_yaml(self.manifest_location, self.manifest)

    def _read_manifest(self):
        return self.datastore.read_yaml(self.manifest_location)

    def write(self, data, metadata, version_name=None, **artifact_write_kwargs):
        # todo add save_mode
        # TODO crash if version_name class changes from previous versions
        # TODO crash if artifact class changes from previous versions
        # TODO collect version metadata
        # todo lock

        if version_name is None:
            prev_version_name = self.latest_version_name(raise_if_none=False)
            version_name = self.version_name_class.next(prev_version_name)

        artifact = self.artifact_class(data, metadata)
        version_manifest = VersionManifest({})
        version = Version(version_name, artifact, version_manifest)
        version.write(self.datastore, self.versions_location, **artifact_write_kwargs)
        self._register_version_name(version_name)

        return version

    def all_version_names(self) -> List[VersionName]:
        """Get all locked (and existing) artifact version names.

        Locked versions might not be existing yet, they are just reserved names.

        Returns
        -------
        List[VersionName]
            A list of all locked version names
        """
        try:
            raw_versions = json.loads(self.datastore.read(self.versions_list_location))
        except FileNotFoundError:
            raw_versions = []
        versions = [VersionName.from_string(raw_version) for raw_version in list(raw_versions)]
        return sorted(versions)

    def version_names(self) -> List[VersionName]:
        """Get all existing artifact version names.

        Versions are considered as "existing" as soon as they have a "manifest.yml"

        Returns
        -------
        List[VersionName]
            A list of all existing version names
        """
        # todo create version_exists
        return [
            name for name in self.all_version_names()
            if self.datastore.exists(
                version_manifest_location(
                    version_location(self.versions_location, name)
                )
            )
        ]

    def latest_version_name(self, raise_if_none=True) -> VersionName:
        """Get the name of the latest version. If none is defined, will raise an exception
        Raises
        ------
        ArtifactHasNoVersion
            If the artifact has no latest version
        Returns
        -------
        VersionName
            The name of the latest version
        """
        versions = self.version_names()
        if not versions:
            if raise_if_none:
                raise ArtifactHasNoVersion(self.location)
            else:
                return None
        return versions[-1]

    def latest_version(self) -> Version:
        """Get the latest version. If none is defined, will raise an exception

        Raises
        ------
        TableHasNoVersion
            If the artifact has no latest version

        Returns
        -------
        Version
            The latest version of this artifact
        """
        return self.read(self.latest_version_name())

    def read(self, version_name: Union[str, VersionName, None] = None) -> Version:
        """Get a specific existing version or the latest one if an empty string is passed

        Parameters
        ----------
        version_name: Union[str, VersionName], optional
            Name of the version to return. If None or "" (empty string), the latest version will
            be returned

        Raises
        ------
        ArtifactHasNoVersion
            If the latest version was requested and the artifact has no version
        ArtifactVersionDoesNotExist
            If the requested version does not exist

        Returns
        -------
        Version
            The request version or the latest if none was requested
        """

        if version_name:
            if isinstance(version_name, str):
                version_name = self.version_name_class.from_string(version_name)
            # todo: check that version_name matches self.version_name_class
        else:
            version_name = self.latest_version_name()

        version = Version.read(
            version_name=version_name,
            artifact_class=self.artifact_class,
            datastore=self.datastore,
            location=self.versions_location,
        )
        #if not version.exists():
        #    raise ArtifactVersionDoesNotExist(self.location, str(version_name))

        return version

    def delete_version(self, version_name: Union[str, VersionName]) -> None:
        """Delete a version, will not fail if the version did not exist

        Parameters
        ----------
        version_name: Union[str, VersionName]
            Name of the version to delete
        """
        if not isinstance(version_name, VersionName):
            version_name = VersionName.from_string(version_name)

        self.datastore.delete(version_location(self.location, version_name), recursive=True)

        # todo: need to lock versions.json here
        names = self.all_version_names()
        if version_name in names:
            names.remove(version_name)
        self._write_version_names(names)
        # todo: need to unlock versions.json here

    def create_version(self,
                       version_name: Union[str, VersionName] = '',
                       save_mode: WriteMode = WriteMode.ERROR_IF_EXISTS) -> Optional[Version]:
        """Creates a version (either a new one or overwrite/append to an existing one)

        Parameters
        ----------
        version_name: Union[str, VersionName] = ''
            Name of the new version. If not specified, a new version name is automatically computed
            based on the current latest (this is safe to use even if it is the first version).
        save_mode: WriteMode = WriteMode.ERROR_IF_EXISTS
            Defines how to behave if the version already exist. ERROR_IF_EXISTS is the default and
            recommended behavior. if you want to overwrite a version you have to explicitly set it
            to WriteMode.OVERWRITE.
        """
        if not version_name:
            name = self._create_version_name()
        else:
            if not isinstance(version_name, VersionName):
                version_name = VersionName.from_string(version_name)
            name = self._register_version_name(version_name)

        version: Optional[Version]
        version = Version(name, version_location(self.location, name), self.datastore)

        # todo: manage the case where the version we want to create is in creation (manifest
        #  does not exist but files are being written by another process).
        if version.exists():
            if save_mode == WriteMode.ERROR_IF_EXISTS:
                raise ArtifactVersionAlreadyExists(version.location)
            elif save_mode == WriteMode.IGNORE:
                logger.info(f"ignoring already existing version at: {version.location}")
                version = None
            elif save_mode == WriteMode.OVERWRITE:
                logger.info(f"deleting partitions at: {version.location}")
                self.datastore.delete(version.location, recursive=True)

        return version

    def _create_version_name(self, retry: bool = True) -> VersionName:
        versions_lock_file = versions_lock_file_location(self.location)
        if self.datastore.exists(versions_lock_file):
            # In case another process just created the data dir and did non update yet the versions
            # list, let's wait a little and retry once
            if retry:
                time.sleep(NEW_VERSION_WAIT_MS / 1000)
                return self._create_version_name(False)
            else:
                raise ArtifactVersionsIsLocked(self.location)
        # todo: this is not safe in case of concurrency.
        self.datastore.write_string(versions_lock_file, '')
        try:
            names = self.all_version_names()
            name = names[-1].next() if names else FIRST_VERSION_NAME
            new_version_name = self._register_version_name(name)
        finally:
            self.datastore.delete(versions_lock_file)

        return new_version_name

    def _register_version_name(self, name: VersionName) -> VersionName:
        # todo: need to lock versions.json here
        names = self.all_version_names()

        if name not in names:
            names.append(name)
            self._write_version_names(names)
            # todo: need to unlock versions.json here

        return name

    def _write_version_names(self, names: List[VersionName]) -> None:
        """Sort, serialize and write version names"""
        strings = [str(name) for name in sorted(names)]
        self.datastore.write_json(self.versions_list_location, strings)
