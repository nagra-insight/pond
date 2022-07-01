from abc import ABC, abstractmethod
from io import BytesIO


class Datastore(ABC):

    @abstractmethod
    def read(self, path: str) -> BytesIO:
        """Read a sequence of bytes from the data store.

        Parameters
        ----------
        path: str
            Path relative to the root of the data store.

        Returns
        -------
        BytesIO
            The sequence of bytes read from `path`.

        Raises
        ------
        FileNotFoundError
            If the requested path does not exist.
        """
        pass

    @abstractmethod
    def write(self, path: str, data: BytesIO) -> None:
        """Write a sequence of bytes to the data store.

        `path` contains the path relative to the root of the data store, including the name
        of the file to be created. If a file already exists at `path`, it is overwritten.

        Parameters
        ----------
        path: str
            Path relative to the root of the data store.
        data: BytesIO
            Sequence of bytes to write at `path`.

        Raises
        ------
        FileNotFoundError
            If the path where the data is to be written does not exist (excluding file name).
        """
        pass

    def delete(self, path: str, recursive: bool = False) -> None:
        """Deletes a file or directory
        Parameters
        ----------
        path: str
            Path relative to the root of the data store.
        recursive: bool, optional, default is False
            Wether to recursively delete the location
        """
        pass
