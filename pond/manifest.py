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

"""


class VersionManifest:
    def __init__(self):
        pass
