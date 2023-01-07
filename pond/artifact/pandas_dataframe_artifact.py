import pandas as pd

from pond.artifact import Artifact


class PandasDataFrameArtifact(Artifact):
    """ Artifact for Pandas DataFrames.
    """

    @classmethod
    def read(cls, file_, **kwargs):
        """ Read a Pandas DataFrame artifact from CSV file. """
        metadata = {}
        while file_.read(1) == '#':
            line = file_.readline()
            key, value = line.strip().split(' ', 1)
            metadata[key] = value
        file_.seek(0)

        data = pd.read_csv(file_, comment='#', **kwargs)
        return cls(data, metadata)

    def write(self, file_, **kwargs):
        for key, value in self.metadata.items():
            txt = f'# {key} {value}\n'
            file_.write(txt)
        self.data.to_csv(file_, **kwargs)
