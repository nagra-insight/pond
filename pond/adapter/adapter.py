from abc import ABC, abstractmethod
from typing import Dict, Generic, TypeVar, Any

from pond.version import Version

DataType = TypeVar('DataType')


class Adapter(ABC, Generic[DataType]):
    @abstractmethod
    def read(self, version: Version) -> DataType:
        pass

    @abstractmethod
    def write(self, data: DataType, version: Version) -> Dict[str, Any]:
        pass
