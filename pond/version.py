from typing import Optional

from pond.conventions import manifest_location
from pond.storage.datastore import Datastore
from pond.version_name import VersionName



class Version:
    def __init__(self, name: VersionName, location: str, store: Datastore):
        """The Version class manages the various elements of a version: its manifest,
        data location, and partition list.

        Parameters
        ----------
        name: VersionName
            Name of the version
        location: str
            URI of the version location
        datastore: DataStore
            DataStore instance
        """
        self.name = name
        self.location = location
        self.store = store

        #: str: location of the manifest file
        self.manifest_location = manifest_location(location)

        # In-memory version of the manifest, defined if it exists and has been read
        self._manifest: Optional[Manifest] = None

    def exists(self) -> bool:
        """Checks whether the version exists.

        A version exists if a manifest.yml file exists in the appropriate location.

        Returns
        -------
        bool
            True if the version exists, False otherwise
        """
        return self._manifest is not None or self.store.exists(self.manifest_location)
