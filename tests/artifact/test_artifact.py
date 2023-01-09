from pond.artifact import Artifact


class MockArtifact(Artifact):
    @classmethod
    def read_bytes(cls, file_, **kwargs):
        return file_.name, kwargs

    def write_bytes(self, file_, **kwargs):
        return file_.name, kwargs

    @staticmethod
    def filename(basename):
        return basename


def test_read(tmp_path):
    kwargs = {'c': 3}
    path = str(tmp_path / "filename.ext")
    with open(path, 'wb') as f:
        f.write(b'abc')

    filename, passed_kwargs = MockArtifact.read(path, **kwargs)
    # check that read_bytes has been called with the right arguments
    assert filename == path
    assert passed_kwargs == kwargs


def test_write(tmp_path):
    data = [1, 2, 3]
    metadata = {'a': 'b'}
    artifact = MockArtifact(data, metadata)

    kwargs = {'c': 3}
    path = str(tmp_path / "filename.ext")
    filename, passed_kwargs = artifact.write(path, **kwargs)
    # check that write_bytes has been  called with the right arguments
    assert filename == path
    assert passed_kwargs == kwargs
