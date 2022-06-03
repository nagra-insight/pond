from typing import Generic, Optional, Union, Sequence, Dict

from pond.version_name import VersionName

from .adapter import Adapter, DataType, SaveMode
from .storage import Datastore


class Activity(Generic[DataType]):
    def __init__(self, source: str, datastore: Datastore, author: str):
        pass

    def read(self,
             name: str,
             adapter: Union[Adapter[DataType], str],
             version_name: Optional[Union[str, VersionName]] = None,
             namespace: str = None) -> DataType:
        pass

    def write(data: DataType,
              name: str,
              adapter: Union[Adapter[DataType], str],
              version_name: Optional[Union[str, VersionName]] = None,
              namespace: str = None,
              inputs: Optional[Sequence[str]] = None,
              metadata: Optional[Dict[str, str]] = None,
              save_mode: SaveMode = SaveMode.ERROR_IF_EXISTS) -> None:
        pass

    # def export()
