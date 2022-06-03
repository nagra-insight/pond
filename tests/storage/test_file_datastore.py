from pond.storage.file_datastore import FileDatastore


def test_file_datastore_read(tmp_path):
    content = b'A test! 012'
    filename = "mydata.bin"
    filepath = tmp_path / filename
    filepath.write_bytes(content)

    ds = FileDatastore(tmp_path)
    data = ds.read(filename)

    assert data == content


def test_file_datastore_write(tmp_path):
    data = b'A test! 012'
    filename = "mydata.bin"

    ds = FileDatastore(tmp_path)
    ds.write(filename, data)

    filepath = tmp_path / filename
    content = filepath.read_bytes()

    assert data == content
