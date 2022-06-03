from abc import abstractmethod
from io import BytesIO
from typing import Optional


class ArtifactStore:
    @abstractmethod
    def read(self, experiment: str, name: str, version_name: Optional[str],
             filename: str) -> BytesIO:
        pass

    @abstractmethod
    def write(self, relative_path: str, data: BytesIO) -> None:
        pass
