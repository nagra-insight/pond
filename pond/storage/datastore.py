from abc import ABC, abstractmethod
from io import BytesIO


class Datastore(ABC):
    @abstractmethod
    def read(self, relative_path: str) -> BytesIO:
        pass

    @abstractmethod
    def write(self, relative_path: str, data: BytesIO) -> None:
        pass
