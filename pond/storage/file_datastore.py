from io import BytesIO
import os

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

    def read(self, path: str) -> BytesIO:
        path = os.path.join(self.base_path, path)
        with open(path, 'rb') as f:
            data = f.read()
        return data

    def write(self, path: str, data: BytesIO) -> None:
        path = os.path.join(self.base_path, path)
        with open(path, 'wb') as f:
            f.write(data)
