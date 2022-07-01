from pond.conventions import TXT_ENCODING
from pond.storage.datastore import Datastore



class DummyDataStore(Datastore):
    def __init__(self, read_content):
        self.read_content = read_content

    def read(self, path):
        return self.read_content.encode(TXT_ENCODING)

    def write(self, path, data):
        self.read_content = data.decode(TXT_ENCODING)

    def exists(self, uri):
        pass


def test_read_string():
    read_content = 'æɝ'
    store = DummyDataStore(read_content)
    str_ = store.read_string('dummy')
    assert str_ == read_content


def test_write_string():
    store = DummyDataStore('')
    content = 'æɝ'
    store.write_string('dummy/path', content)
    read_content = store.read_string('dummy/path')
    assert read_content == content


def test_read_yaml():
    read_content = """
value: æɝ
version: 2021-02-03
    """.strip()

    store = DummyDataStore(read_content)
    dict_ = store.read_yaml('dummy')

    expected = {
        'value': 'æɝ',
        'version': '2021-02-03',
    }
    assert dict_ == expected


def test_write_yaml():
    content = {
        'value': 'æɝ',
        'version': '2021-02-03',
    }
    store = DummyDataStore('')
    store.write_yaml('dummy', content)
    read_content = store.read_yaml('dummy')

    assert read_content == content
