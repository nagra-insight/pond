from typing import Optional, Union

from pond.adapter import SaveMode
from pond.entities import DataKind
from pond.storage.datastore import Datastore
from pond.version import Version
from pond.version_name import VersionName


class Artefact:
    def __init__(self, datastore: Datastore, relative_path: str):
        self.store = datastore
        self.path = relative_path

        self.data_kind = DataKind.DATA_FRAME

        self.versions_location = f'{self.path}/versions.json'

    def create_version(self,
                       version_name: Union[str, VersionName] = '',
                       save_mode: SaveMode = SaveMode.ERROR_IF_EXISTS) -> Optional[Version]:
        pass
