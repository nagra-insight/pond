from abc import abstractmethod


class MetadataSource:

    @abstractmethod
    def section_name(self):
        """ Name of the section in the manifest corresponding to this metadata. """
        return ''

    @abstractmethod
    def collect(self):
        return {}


class DictMetadataSource(MetadataSource):

    def __init__(self, name: str, metadata: dict):
        self.name = name
        self.metadata = metadata

    def section_name(self):
        return self.name

    def collect(self):
        return self.metadata
