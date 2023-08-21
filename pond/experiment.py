from typing import Union, Optional, Sequence, Dict

from pond.activity import Activity
from pond.adapter import Adapter, DataType, SaveMode
from pond.version_name import RunVersionName, VersionName


class ExperimentWithRuns:
    def __init__(self, activity: Activity, experiment_id: str, run_id: Optional[str] = None):
        self.activity = activity
        self.experiment_id = experiment_id
        if run_id is not None:
            # cannot create a new run using the initialized
            self.set_run(run_id)
        # version_name = RunVersionName(run_id=self.run_id, version_number=1)
        # self.current_run_version_name: RunVersionName =

    def create_run(self, run_id):
        # raise if run_id exists already
        self.run = RunVersionName(run_id=run_id)

    def set_run(self, run_id):
        # raise if `run_id` does not exist
        pass

    def get_available_runs(self):
        # returns list of available runs for this experiment
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
