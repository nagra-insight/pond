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
    def read(cls, path, metadata=None, **kwargs):
        """ Reads the artifact from file.

        Parameters
        ----------
        path: str
            Filename from which the artifact is read.
        kwargs: dict
            Parameters for the reader.
        metadata: dict or None
            The metadata for the artifact. If defined, it takes the place of any metadata
            defined in the artifact itself.
            Typically, this external artifact metadata comes from an artifact manifest. If the
            artifact has been written as a `pond` `Version`, then the two sources of metadata
            are identical.

        Returns
        -------
        artifact: Artifact
            An instance of the artifact.
        """
        with open(path, 'rb') as f:
            artifact = cls.read_bytes(f, **kwargs)
        if metadata is not None:
            artifact.metadata = metadata
        return artifact

    def write(self, path, **kwargs):
        """ Writes the artifact to file.

        Parameters
        ----------
        path: str
            Path to which the artifact is written.
        kwargs: dict
            Parameters for the writer.

        """
        with open(path, 'wb') as f:
            self.write_bytes(f, **kwargs)

    # --- Abstract interface

    @staticmethod
    @abstractmethod
    def filename(basename):
        """ Complete a base filename with an extension.

        Parameters
        ----------
        basename: str
            The filename without extension.

        Returns
        -------
        filename: str
            The completed filename.

        """
        pass

    @classmethod
    @abstractmethod
    def read_bytes(cls, file_, **kwargs):
        """ Reads the artifact from a binary file.

        Parameters
        ----------
        file_: file-like object
            A file-like object from which the artifact is read, opened in binary mode.
        kwargs: dict
            Parameters for the reader.

        Returns
        -------
        artifact: Artifact
            An instance of the artifact.
        """
        pass

    @abstractmethod
    def write_bytes(self, file_, **kwargs):
        """ Writes the artifact to binary file.

        Parameters
        ----------
        file_: file-like object
            A file-like object to which the artifact is written, opened in binary mode.
        kwargs: dict
            Parameters for the writer.

        """
        pass
