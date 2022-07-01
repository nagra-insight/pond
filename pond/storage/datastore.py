from abc import ABC, abstractmethod
from io import BytesIO
from typing import Any

from pond.conventions import TXT_ENCODING
from pond.yaml import yaml_dump, yaml_load


class Datastore(ABC):

    # -- Abstract interface

    @abstractmethod
    def read(self, path: str) -> BytesIO:
        """ Read a sequence of bytes from the data store.

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
        """ Write a sequence of bytes to the data store.

        `path` contains the path relative to the root of the data store, including the name
        of the file to be created. If a file already exists at `path`, it is overwritten.

        Intermediate directories that do not exist will be created.

        Parameters
        ----------
        path: str
            Path relative to the root of the data store.
        data: BytesIO
            Sequence of bytes to write at `path`.
        """
        pass

    @abstractmethod
    def exists(self, uri: str) -> bool:
        """ Returns True if the file exists.

        Parameters
        ----------
        uri: str
            URI to the file location, relative to the root of the data store.

        Returns
        -------
        bool
            True if the file exists, false otherwise
        """
        ...

    @abstractmethod
    def delete(self, path: str, recursive: bool = False) -> None:
        """Deletes a file or directory
        Parameters
        ----------
        path: str
            Path relative to the root of the data store.
        recursive: bool, optional, default is False
            Wether to recursively delete the location
        """
        ...

    # -- Read/write utility methods

    def read_string(self, uri: str) -> str:
        """ Read a string from a file.

        Parameters
        ----------
        uri: str
            Location of the file

        Returns
        -------
        str
            The read string

        Raises
        ------
        FileNotFound
            If the file cannot be found
        """
        return self.read(uri).decode(TXT_ENCODING)

    def write_string(self, uri: str, content: str) -> None:
        """ Write a string to a file.

        Intermediate directories that do not exist will be created.

        Parameters
        ----------
        uri: str
            Location of the file

        content: str
            Content to write
        """
        self.write(uri, content.encode(TXT_ENCODING))

    def read_yaml(self, uri: str) -> Any:
        """ Read and parse a JSON file.

        Parameters
        ----------
        uri: str
            Location of the file

        Returns
        -------
        Any
            The parsed object

        Raises
        ------
        FileNotFound
            If the file cannot be found
        """
        # We use `read` instead of `read_string` because the yaml library already takes care
        # of the encoding
        return yaml_load(self.read(uri))

    def write_yaml(self, uri: str, content: Any) -> None:
        """ Serializes to YAML and write an object to a file.

        Intermediate directories that do not exist will be created.

        Parameters
        ----------
        uri: str
            URI to the file location
        content: Any
            Content to write
        """
        # We use `write` instead of `write_string` because the yaml library already takes care
        # of the encoding
        return self.write(uri, yaml_dump(content))
