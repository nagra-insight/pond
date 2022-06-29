from pond.storage.file_datastore import FileDatastore

import pytest


def test_base_path_does_not_exist(tmp_path):
    # path does not exist
    with pytest.raises(FileNotFoundError):
        FileDatastore('does_not_exist')

    # path exists, but it's not a directory
    filename = 'mydata'
    filepath = tmp_path / filename
    filepath.touch()
    with pytest.raises(NotADirectoryError):
        FileDatastore(filepath)


def test_read(tmp_path):
    content = b'A test! 012'
    filename = 'mydata.bin'
    filepath = tmp_path / filename
    filepath.write_bytes(content)

    ds = FileDatastore(tmp_path)
    data = ds.read(filename)

    assert data == content


def test_read_file_not_found(tmp_path):
    ds = FileDatastore(tmp_path)
    with pytest.raises(FileNotFoundError):
        ds.read('does_not_exist')


def test_write(tmp_path):
    data = b'A test! 012'
    filename = 'mydata.bin'
    filepath = tmp_path / filename

    ds = FileDatastore(tmp_path)
    ds.write(filename, data)

    content = filepath.read_bytes()
    assert data == content


def test_write_file_path_does_not_exist(tmp_path):
    data = b'A test! 012'

    ds = FileDatastore(tmp_path)
    with pytest.raises(FileNotFoundError):
        ds.write('does_not_exits/blah', data)
