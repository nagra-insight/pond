from typing import Union, Optional, Sequence, Dict

from pond.activity import Activity
from pond.adapter import Adapter, DataType, SaveMode
from pond.version_name import RunName, VersionName


class Experiment:
    def __init__(self, activity: Activity, name: str):
        self.activity = activity
        self.name = name
        self.run: Optional[RunName] = None

    def create_run(self):
        self.run = RunName()

    def set_run(self, run_id):
        pass

    def read(self,
             name: str,
             adapter: Union[Adapter[DataType], str],
             version_name: Optional[Union[str, VersionName]] = None) -> DataType:
        pass

    def write(self,
              data: DataType,
              name: str,
              adapter: Union[Adapter[DataType], str],
              version_name: Optional[Union[str, VersionName]] = None,
              inputs: Optional[Sequence[str]] = None,
              metadata: Optional[Dict[str, str]] = None,
              save_mode: SaveMode = SaveMode.ERROR_IF_EXISTS):
        pass
