from collections import defaultdict, namedtuple

from pond.exceptions import ArtifactNotFound, FormatNotFound


ArtifactRegistryItem = namedtuple('ArtifactRegistryItem', ['artifact_class', 'format'])


class ArtifactRegistry:
    """ Registry of data types to compatible artifact classes. """

    def __init__(self):
        self._register = defaultdict(list)

    def register(self, data_class, artifact_class, format=None):
        item = ArtifactRegistryItem(artifact_class=artifact_class, format=format)
        self._register[data_class].append(item)

    def get_artifact(self, data_class, format=None):
        """
        In case multiple artifacts are available for the same data class and format,
        the last registered artifact is returned.

        Parameters
        ----------
        data_class: class
            Data class for which we need to find an adapter.
        format: str
            We require an adapter that can handle this file format.

        Returns
        -------
        artifact_class: class
            Artifact class

        """
        items = self._register[data_class]
        if len(items) == 0:
            raise ArtifactNotFound(data_class)

        if format is None:
            artifact_class = items[-1].artifact_class
        else:
            for item in items:
                if item.format == format:
                    artifact_class = item.artifact_class
                    break
            else:
                raise FormatNotFound(data_class, format)

        return artifact_class

    def get_formats_for_data(self, data_class):
        pass


global_artifact_registry = ArtifactRegistry()
