import os.path

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


def test_write_intermediate_paths_created(tmp_path):
    data = b'A test! 012'
    filename = 'mydata.bin'
    filepath = f'a/b/{filename}'

    ds = FileDatastore(tmp_path)
    ds.write(filepath, data)

    assert ds.exists(filepath)


def test_write_path_relative_datastore_path(tmp_path):
    from tempfile import TemporaryDirectory
    # There used to be a bug with writing when the datastore path was defined in a relative way
    data = b'A test! 012'
    filename = 'mydata.bin'
    filepath = f'a/b/{filename}'

    with TemporaryDirectory(dir='.') as tmpdirname:
        print('created temporary directory', tmpdirname)
        ds = FileDatastore(tmpdirname)
        ds.write(filepath, data)

        assert ds.exists(filepath)



def test_exists(tmp_path):
    ds = FileDatastore(tmp_path)
    assert ds.exists(str(tmp_path))

    filename = 'data.bin'
    # Location is the *absolute* path, not relative to the Datastore
    location = str(tmp_path / filename)
    assert not ds.exists(location)

    ds.write(filename, b'something')
    assert ds.exists(location)


def test_makedirs(tmp_path):
    ds = FileDatastore(tmp_path)
    create_path = os.path.join('a', 'b')

    expected_path = tmp_path / create_path
    assert not os.path.exists(expected_path)
    ds.makedirs(str(create_path))
    assert os.path.exists(expected_path)


def test_open(tmp_path):
    ds = FileDatastore(tmp_path)
    filename = 'something.bin'

    assert not ds.exists('something.bin')
    with ds.open(filename, 'wb') as f:
        f.write(b'abc')
    assert ds.exists('something.bin')
