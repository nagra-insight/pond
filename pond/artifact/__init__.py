from abc import ABC, abstractmethod


class Artifact(ABC):
    """ Knows how to read and write one type of artifact.

    Concrete Artifact implementation should save the metadata with the data if possible,
    so that the artifact is self-contained even, for instance, if it sent by email.
    """

    def __init__(self, data, metadata=None):
        """ Create an Artifact.

        Parameters
        ----------
        data: any
            The data of the artifact.
        metadata: dict
            A dictionary of the metadata saved with the artifact (optional).
        """
        self.data = data
        if metadata is None:
            metadata = {}
        self.metadata = metadata

    @classmethod
    @abstractmethod
    def read(cls, file_, **kwargs):
        """ Reads the artifact from file.

        Parameters
        ----------
        file_: file-like object
            A file-like object from which the artifact is read, opened in `rb` mode.
        kwargs: dict
            Parameters for the reader.

        Returns
        -------
        artifact: Artifact
            An instance of the artifact.
        """
        pass

    @abstractmethod
    def write(self, file_, **kwargs):
        """ Writes the artifact to file.

        Parameters
        ----------
        file_: file-like object
            A file-like object to which the artifact is written, opened in `wb` mode.
        kwargs: dict
            Parameters for the writer.

        """
        pass
