import json
import logging
import time
from typing import List, Optional, Union

from pond.adapter import SaveMode
from pond.conventions import manifest_location, version_location, version_lock_file_location
from pond.entities import DataKind
from pond.exceptions import ArtifactHasNoVersion, ArtifactVersionAlreadyExists, \
    ArtifactVersionDoesNotExist, ArtifactVersionIsLocked
from pond.storage.datastore import Datastore
from pond.version import Version
from pond.version_name import SimpleVersionName, VersionName

logger = logging.getLogger(__name__)

# Time to wait before retrying when creating a new version fails
NEW_VERSION_WAIT_MS = 1000

# a default version when no version is specified for the first version of an artifact
FIRST_VERSION_NAME = SimpleVersionName(1)


class Artifact:

    def __init__(self, datastore: Datastore, location: str):
        self.store = datastore
        self.location = location
        self.versions_location = f'{self.location}/versions.json'

        self.data_kind = DataKind.DATA_FRAME

    def all_version_names(self) -> List[VersionName]:
        """Get all locked (and existing) artifact version names.
        Locked versions might not be existing yet, they are just reserved names.
        Returns
        -------
        List[VersionName]
            A list of all locked version names
        """
        try:
            raw_versions = json.load(self.store.read(self.versions_location))
        except FileNotFoundError:
            raw_versions = []
        versions = [VersionName.parse(raw_version) for raw_version in list(raw_versions)]
        return sorted(versions)

    def version_names(self) -> List[VersionName]:
        """Get all existing artifact version names.
        Versions are considered as "existing" as soon as they have a "manifest.yml"
        Returns
        -------
        List[VersionName]
            A list of all existing version names
        """
        return [
            name for name in self.all_version_names()
            if self.store.exists(manifest_location(version_location(self.location, name)))
        ]

    def latest_version_name(self) -> VersionName:
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
            raise ArtifactHasNoVersion(self.location)
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
        return self.version(self.latest_version_name())

    def version(self, version_name: Union[str, VersionName, None] = None) -> Version:
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
            if not isinstance(version_name, VersionName):
                version_name = VersionName.parse(version_name)
            version = Version(name=version_name,
                              location=version_location(self.location, version_name),
                              store=self.store)
            if not version.exists():
                raise ArtifactVersionDoesNotExist(self.location, str(version_name))
        else:
            version = self.latest_version()

        return version

    def delete_version(self, version_name: Union[str, VersionName]) -> None:
        """Delete a version, will not fail if the version did not exist
        Parameters
        ----------
        version_name: Union[str, VersionName]
            Name of the version to delete
        """
        if not isinstance(version_name, VersionName):
            version_name = VersionName.parse(version_name)

        self.store.delete(version_location(self.location, version_name), recursive=True)

        # todo: need to lock versions.json here
        names = self.all_version_names()
        if version_name in names:
            names.remove(version_name)
        self._write_version_names(names)
        # todo: need to unlock versions.json here

    def create_version(self,
                       version_name: Union[str, VersionName] = '',
                       save_mode: SaveMode = SaveMode.ERROR_IF_EXISTS) -> Optional[Version]:
        """Creates a version (either a new one or overwrite/append to an existing one)
        Parameters
        ----------
        version_name: Union[str, VersionName] = ''
            Name of the new version. If not specified a new version name is automatically computed
            based on the current latest (this is safe to use even if it is the first version).
        save_mode: SaveMode = SaveMode.ERROR_IF_EXISTS
            Defines how to behave if the version already exist. ERROR_IF_EXISTS is the default and
            recommended behavior. if you want to overwrite a version you have to explicitly set it
            to SaveMode.OVERWRITE.
        """
        if not version_name:
            name = self._create_version_name()
        else:
            if not isinstance(version_name, VersionName):
                version_name = VersionName.parse(version_name)
            name = self._register_version_name(version_name)

        version: Optional[Version]
        version = Version(name, version_location(self.location, name), self.store)

        if version.exists():
            if save_mode == SaveMode.ERROR_IF_EXISTS:
                raise ArtifactVersionAlreadyExists(version.location)
            elif save_mode == SaveMode.IGNORE:
                logger.info(f"ignoring already existing version at: {version.data_location}")
                version = None
            elif save_mode == SaveMode.OVERWRITE:
                logger.info(f"deleting partitions at: {version.data_location}")
                self.store.delete(version.data_location, recursive=True)
                self.store.delete(version.partitions_location, recursive=False)
                self.store.delete(version.manifest_location, recursive=False)

        return version

    def _create_version_name(self, retry: bool = True) -> VersionName:
        names = self.all_version_names()  # cache current version names
        name = names[-1].next() if names else FIRST_VERSION_NAME
        version_loc = version_location(self.location, name)
        version_lock_file = version_lock_file_location(version_loc)

        if self.store.exists(version_lock_file):
            # In case another process just created the data dir and did non update yet the versions
            # list, let's wait a little and retry once
            if retry:
                time.sleep(NEW_VERSION_WAIT_MS / 1000)
                return self._create_version_name(False)
            else:
                raise ArtifactVersionIsLocked(version_loc)

        # todo: need to delete the lock file when manifest is written
        self.store.write_string(version_lock_file, '')
        return self._register_version_name(name)

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
        self.store.write_json(self.versions_location, strings)
