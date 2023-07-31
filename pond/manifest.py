"""

# Manifest related attributes
manifest_version: 1

# Identification attributes
id: 'pond://<namespace>/<artefact>/<version>'
# ... detail every part

# General information
author: author.email@host.com
source: <source-URI>
date_time: <yyyy-MM-dd HH:mm:ss>
inputs:
  - catalog://database/table/v1
  - https://github.com/organ/project/blob/master/configuration.yaml


adapter_id: mpl
adapter_metadata:
  # ...

run_metadata:
  # ...

user_metadata:
  # ...





store/
    default/
        artifact/
            v1/
                _pond/
                    _LOCK
                    manifest.yml
                # ...
    experiment_1/
        _pond/
            experiment.yml
            run2.yml
        artifact/
            run=2&v=1/
                _pond/
                    _LOCK
                    manifest.yml
                # ...


store/
        artifact_name/
            v1/
                _pond/
                    _LOCK
                    manifest.yml
                data/
                    data.ext
                # ...

"""
from pond.artifact import Artifact
from pond.storage.datastore import Datastore


class ArtifactManifest:
    """ Artifact metadata is mostly free-form, user-defined entries. """

    def __init__(self, metadata: dict):
        self.metadata = metadata

    @classmethod
    def from_artifact(cls, artifact: Artifact):
        return cls(artifact.metadata)

    @classmethod
    def from_yaml(cls, location: str, datastore: Datastore):
        dict_ = datastore.read_yaml(location)
        return cls(dict_['metadata'])

    def to_dict(self):
        dict_ = {
            'metadata': self.metadata,
        }
        return dict_

    def write_yaml(self, location: str, datastore: Datastore):
        datastore.write_yaml(location, self.to_dict())


class _VersionManifest:
    """ Version metadata contains all the information about the stored artifact,
    and the context in which it was stored. """

    VERSION = 1

    def __init__(self, artifact_id: str, author: str, source: str, date_time: str, inputs: list):
        self.artifact_id = artifact_id

    @classmethod
    def from_version(cls, version: "Version"):
        return cls()


class VersionManifest:
    """ At the moment, just a dummy implementation. """

    def __init__(self, dict_):
        self.dict_ = dict_

    def to_dict(self):
        # TODO should this be a copy
        return self.dict_
