from io import BytesIO
import os
from shutil import rmtree

from pond.storage.datastore import Datastore


class FileDatastore(Datastore):
    """Datastore based on a regular file system.

    Parameters
    ----------
    base_path: str
        Filesystem path at which the data store is based.

    Raises
    ------
    FileNotFoundError
        If `base_path` does not exists.
    NotADirectoryError
        If `base_path` exists but is not a directory.
    """

    def __init__(self, base_path: str):
        if not os.path.exists(base_path):
            raise FileNotFoundError(f'Base path {base_path} does not exist')
        if not os.path.isdir(base_path):
            raise NotADirectoryError(f'Base path {base_path} exists but is not a directory')

        self.base_path = base_path

    # -- Datastore interface

    def read(self, path: str) -> BytesIO:
        path = os.path.join(self.base_path, path)
        with open(path, 'rb') as f:
            data = f.read()
        return data

    def write(self, path: str, data: BytesIO) -> None:
        path = os.path.join(self.base_path, path)
        self.create_dir(os.path.dirname(path))
        with open(path, 'wb') as f:
            f.write(data)

    def exists(self, uri: str) -> bool:
        """ Returns True if the file exists.

        Parameters
        ----------
        uri: str
            URI to the file location, relative to the root of the data store.
            In the FileDatastore implementation, `uri` can also be an absolute path including
            the root of the data store.

        Returns
        -------
        bool
            True if the file exists, false otherwise
        """
        complete_uri = os.path.join(self.base_path, uri)
        return os.path.exists(complete_uri)

    def delete(self, path: str, recursive: bool = False) -> None:
        if os.path.exists(path):
            if recursive:
                rmtree(path)
            else:
                os.remove(path)

    # -- FileDatastore interface

    def create_dir(self, uri: str) -> None:
        """ Creates the specified directory if needed.

        Parameters
        ----------
        uri: str
            URI to the directory to create
        """
        os.makedirs(uri, exist_ok=True)
