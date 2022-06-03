from abc import abstractmethod


class VersionName:
    @abstractmethod
    def next():
        pass


class SimpleVersionName(VersionName):
    def __init__(self, version: int):
        pass


class VersionNameWithRun(VersionName):
    def __init__(self, run_id: str, version_name: VersionName) -> None:
        pass


class RunName:
    def __init__(self, version: int = 1, base_name: str = 'run_'):
        pass
