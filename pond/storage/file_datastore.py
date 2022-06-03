from io import BytesIO
import os

from pond.storage.datastore import Datastore


class FileDatastore(Datastore):

    def __init__(self, base_path: str):
        if not os.path.isdir(base_path):
            raise RuntimeError(f'Base path {base_path} does not exist')
        self.base_path = base_path

    def read(self, relative_path: str) -> BytesIO:
        path = os.path.join(self.base_path, relative_path)
        with open(path, 'rb') as f:
            data = f.read()
        return data

    def write(self, relative_path: str, data: BytesIO) -> None:
        path = os.path.join(self.base_path, relative_path)
        with open(path, 'wb') as f:
            f.write(data)
