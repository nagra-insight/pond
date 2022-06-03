from pond.storage.file_datastore import FileDatastore

import pytest


def test_file_datastore_read(tmp_path):
    content = b'A test! 012'
    filename = 'mydata.bin'
    filepath = tmp_path / filename
    filepath.write_bytes(content)

    ds = FileDatastore(tmp_path)
    data = ds.read(filename)

    assert data == content


def test_file_datastore_path_does_not_exist(tmp_path):
    # path does not exist
    with pytest.raises(RuntimeError):
        FileDatastore('does_not_exist')

    # path exists, but it's a file
    filename = 'mydata'
    filepath = tmp_path / filename
    filepath.touch()

    with pytest.raises(RuntimeError):
        FileDatastore(filepath)


def test_file_datastore_write(tmp_path):
    data = b'A test! 012'
    filename = 'mydata.bin'

    ds = FileDatastore(tmp_path)
    ds.write(filename, data)

    filepath = tmp_path / filename
    content = filepath.read_bytes()

    assert data == content
